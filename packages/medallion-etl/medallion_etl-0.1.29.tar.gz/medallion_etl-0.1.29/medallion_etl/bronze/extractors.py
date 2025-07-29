"""Extractores para la capa Bronze de Medallion ETL."""

import io
import json
from pathlib import Path
from typing import Any, Dict, Optional, Union
import polars as pl
import requests
from sqlalchemy import create_engine, text

from medallion_etl.core import Task, TaskResult
from medallion_etl.config import config


class FileExtractor(Task[str, pl.DataFrame]):
    """Extractor base para archivos."""
    
    def __init__(
        self, 
        name: Optional[str] = None,
        description: Optional[str] = None,
        output_path: Optional[Path] = None,
        save_raw: bool = True
    ):
        super().__init__(name, description)
        self.output_path = output_path or config.bronze_dir
        self.save_raw = save_raw
    
    def save_raw_data(self, file_path: str, data: Any) -> Path:
        """Guarda los datos crudos en el directorio bronze."""
        output_file = self.output_path / Path(file_path).name
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        if isinstance(data, (str, bytes)):
            mode = "wb" if isinstance(data, bytes) else "w"
            with open(output_file, mode) as f:
                f.write(data)
        else:
            with open(output_file, "w") as f:
                json.dump(data, f)
                
        return output_file


class CSVExtractor(FileExtractor):
    """Extractor para archivos CSV."""
    
    def __init__(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        output_path: Optional[Path] = None,
        save_raw: bool = True,
        **csv_options
    ):
        super().__init__(name, description, output_path, save_raw)
        self.csv_options = csv_options
    
    def run(self, input_data: str, **kwargs) -> TaskResult[pl.DataFrame]:
        """Extrae datos de un archivo CSV."""
        # input_data puede ser una ruta a un archivo o una URL
        is_url = input_data.startswith("http") 
        
        if is_url:
            response = requests.get(input_data)
            response.raise_for_status()
            content = response.text
            
            if self.save_raw:
                file_name = input_data.split("/")[-1]
                if not file_name.endswith(".csv"):
                    file_name = f"download_{file_name}.csv"
                saved_path = self.save_raw_data(file_name, content)
            
            df = pl.read_csv(content, **self.csv_options)
        else:
            # Es una ruta de archivo local
            df = pl.read_csv(input_data, **self.csv_options)
            
            if self.save_raw and Path(input_data) != self.output_path:
                saved_path = self.save_raw_data(input_data, open(input_data, "r").read())  # noqa: F841
        
        metadata = {
            "source": input_data,
            "rows": len(df),
            "columns": df.columns,
        }
        
        return TaskResult(df, metadata)


class ParquetExtractor(FileExtractor):
    """Extractor para archivos Parquet."""
    
    def __init__(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        output_path: Optional[Path] = None,
        save_raw: bool = True,
        **parquet_options
    ):
        super().__init__(name, description, output_path, save_raw)
        self.parquet_options = parquet_options
    
    def run(self, input_data: str, **kwargs) -> TaskResult[pl.DataFrame]:
        """Extrae datos de un archivo Parquet."""
        is_url = input_data.startswith("http")
        
        if is_url:
            response = requests.get(input_data)
            response.raise_for_status()
            content = response.content
            
            if self.save_raw:
                file_name = input_data.split("/")[-1]
                if not file_name.endswith(".parquet"):
                    file_name = f"download_{file_name}.parquet"
                saved_path = self.save_raw_data(file_name, content)
            
            # Guardar temporalmente para leer con polars
            temp_file = Path("temp.parquet")
            with open(temp_file, "wb") as f:
                f.write(content)
            
            df = pl.read_parquet(temp_file, **self.parquet_options)
            temp_file.unlink()  # Eliminar archivo temporal
        else:
            # Es una ruta de archivo local
            df = pl.read_parquet(input_data, **self.parquet_options)
            
            if self.save_raw and Path(input_data) != self.output_path:
                saved_path = self.save_raw_data(input_data, open(input_data, "rb").read())  # noqa: F841
        
        metadata = {
            "source": input_data,
            "rows": len(df),
            "columns": df.columns,
        }
        
        return TaskResult(df, metadata)


class APIExtractor(Task[Dict[str, Any], pl.DataFrame]):
    """Extractor de API que soporta respuestas JSON y Parquet."""
    
    def __init__(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        output_path: Optional[Path] = None,
        save_raw: bool = True,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        data_key: Optional[str] = None,
        use_mock: bool = False,              
        mock_file: Optional[str] = None,
        response_format: str = "auto"  # ✅ NUEVO: "auto", "json", "parquet"
    ):
        super().__init__(name, description)
        self.output_path = output_path or config.bronze_dir
        self.save_raw = save_raw
        self.method = method.upper()
        self.headers = headers or {}
        self.data_key = data_key
        self.use_mock = use_mock
        self.mock_file = mock_file
        self.response_format = response_format  # ✅ NUEVO

    def run(self, input_data: Dict[str, Any], **kwargs) -> TaskResult[pl.DataFrame]:
        if self.use_mock and self.mock_file:
            # Usar archivo mockeado (mantiene funcionalidad existente)
            df, metadata = self._handle_mock_data()
        else:
            # Lógica normal de llamada a la API
            df, metadata = self._handle_api_call(input_data)
        
        return TaskResult(df, metadata)
    
    def _handle_mock_data(self) -> tuple[pl.DataFrame, Dict[str, Any]]:
        """Maneja datos mockeados (funcionalidad existente mejorada)."""
        mock_path = Path(self.mock_file)
        
        if mock_path.suffix.lower() == '.json':
            with open(self.mock_file, "r", encoding='utf-8') as f:
                json_data = json.load(f)
            print(f"🧪 Usando mock JSON de {self.mock_file}")
            df = self._json_to_dataframe(json_data)
        elif mock_path.suffix.lower() == '.parquet':
            df = pl.read_parquet(self.mock_file)
            print(f"🧪 Usando mock Parquet de {self.mock_file}")
        else:
            # Fallback para compatibilidad con código existente
            with open(self.mock_file, "r", encoding='utf-8') as f:
                json_data = json.load(f)
            print(f"🧪 Usando mock data de {self.mock_file}")
            df = self._json_to_dataframe(json_data)
        
        metadata = {
            "source": self.mock_file,
            "status_code": 200,
            "rows": len(df),
            "columns": df.columns,
            "format": "mock"
        }
        
        return df, metadata
    
    def _handle_api_call(self, input_data: Dict[str, Any]) -> tuple[pl.DataFrame, Dict[str, Any]]:
        """Maneja llamadas reales a la API con soporte para JSON y Parquet."""
        url = input_data.get("url")
        if not url:
            raise ValueError("Se requiere una URL en el diccionario de entrada")
        
        params = input_data.get("params", {})
        body = input_data.get("body", {})
        headers = {**self.headers, **input_data.get("headers", {})}
        
        # Realizar la llamada a la API
        response = requests.request(
            method=self.method,
            url=url,
            params=params,
            json=body if self.method in ["POST", "PUT", "PATCH"] else None,
            headers=headers,
            timeout=30  # ✅ AGREGADO: timeout por seguridad
        )
        response.raise_for_status()
        
        # Detectar formato de respuesta
        content_type = response.headers.get('content-type', '').lower()
        detected_format = self._detect_response_format(response, content_type)
        
        print(f"🌐 API response: {detected_format.upper()} ({len(response.content)} bytes)")
        
        # Procesar según el formato
        if detected_format == "parquet":
            df = self._handle_parquet_response(response)
        elif detected_format == "json":
            df = self._handle_json_response(response)
        else:
            raise ValueError(f"Formato de respuesta no soportado: {detected_format}")
        
        # Guardar datos crudos si es necesario
        if self.save_raw:
            self._save_raw_response(response, url, detected_format)
        
        metadata = {
            "source": url,
            "status_code": response.status_code,
            "rows": len(df),
            "columns": df.columns,
            "format": detected_format,
            "content_type": content_type
        }
        
        return df, metadata
    
    def _detect_response_format(self, response: requests.Response, content_type: str) -> str:
        """Detecta automáticamente el formato de la respuesta."""
        if self.response_format != "auto":
            return self.response_format
        
        # Detectar por Content-Type
        if 'parquet' in content_type or 'octet-stream' in content_type:
            # Verificar si realmente es parquet por el contenido
            if self._is_parquet_content(response.content):
                return "parquet"
        
        if 'json' in content_type or 'application/json' in content_type:
            return "json"
        
        # Detectar por Content-Disposition (archivo adjunto)
        content_disposition = response.headers.get('content-disposition', '')
        if 'parquet' in content_disposition.lower():
            return "parquet"
        
        # Fallback: intentar detectar por el contenido
        try:
            # Intentar parseear como JSON primero
            response.json()
            return "json"
        except:
            # Si falla JSON, verificar si es Parquet
            if self._is_parquet_content(response.content):
                return "parquet"
        
        # Último fallback
        return "json"
    
    def _is_parquet_content(self, content: bytes) -> bool:
        """Verifica si el contenido es un archivo Parquet válido."""
        try:
            # Los archivos Parquet empiezan con "PAR1"
            if content[:4] == b'PAR1':
                return True
            
            # Intentar leer como Parquet
            parquet_buffer = io.BytesIO(content)
            pl.read_parquet(parquet_buffer)
            return True
        except:
            return False
    
    def _handle_parquet_response(self, response: requests.Response) -> pl.DataFrame:
        """Maneja respuestas en formato Parquet."""
        try:
            # Leer Parquet desde bytes en memoria
            parquet_buffer = io.BytesIO(response.content)
            df = pl.read_parquet(parquet_buffer)
            
            print(f"✅ Parquet parseado: {df.shape[0]} filas, {df.shape[1]} columnas")
            return df
            
        except Exception as e:
            raise ValueError(f"Error parseando respuesta Parquet: {e}")
    
    def _handle_json_response(self, response: requests.Response) -> pl.DataFrame:
        """Maneja respuestas en formato JSON (funcionalidad existente)."""
        try:
            json_data = response.json()
            df = self._json_to_dataframe(json_data)
            
            print(f"✅ JSON parseado: {df.shape[0]} filas, {df.shape[1]} columnas")
            return df
            
        except Exception as e:
            raise ValueError(f"Error parseando respuesta JSON: {e}")
    
    def _json_to_dataframe(self, json_data: Any) -> pl.DataFrame:
        """Convierte datos JSON a DataFrame (funcionalidad existente)."""
        # Extraer datos relevantes si se especifica una clave
        if self.data_key:
            data_to_convert = json_data.get(self.data_key, [])
        else:
            data_to_convert = json_data
        
        # Convertir a DataFrame
        if isinstance(data_to_convert, list):
            df = pl.DataFrame(data_to_convert, strict = False) if data_to_convert else pl.DataFrame()
        elif isinstance(data_to_convert, dict):
            df = pl.DataFrame([data_to_convert], strict = False)
        else:
            raise ValueError(f"No se pueden convertir los datos a DataFrame: {type(data_to_convert)}")
        
        return df
    
    def _save_raw_response(self, response: requests.Response, url: str, format_type: str):
        """Guarda la respuesta cruda en el formato apropiado."""
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        # Determinar extensión según el formato
        if format_type == "parquet":
            extension = ".parquet"
            mode = "wb"
            content = response.content
        else:  # json
            extension = ".json"
            mode = "w"
            content = json.dumps(response.json(), indent=2)
        
        # Crear nombre de archivo
        url_part = url.split('/')[-1] or "api_response"
        file_name = f"{self.name or 'api'}_{url_part}{extension}"
        
        # Guardar archivo
        file_path = self.output_path / file_name
        with open(file_path, mode, encoding='utf-8' if mode == 'w' else None) as f:
            f.write(content)
        
        print(f"💾 Datos crudos guardados: {file_name}")


class SQLExtractor(Task[Dict[str, Any], pl.DataFrame]):
    """Extractor para bases de datos SQL."""
    
    def __init__(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        output_path: Optional[Path] = None,
        save_raw: bool = True,
        connection_string: Optional[str] = None,
    ):
        super().__init__(name, description)
        self.output_path = output_path or config.bronze_dir
        self.save_raw = save_raw
        self.connection_string = connection_string
    
    def run(self, input_data: Dict[str, Any], **kwargs) -> TaskResult[pl.DataFrame]:
        """Extrae datos de una base de datos SQL."""
        # Obtener la consulta SQL
        query = input_data.get("query")
        if not query:
            raise ValueError("Se requiere una consulta SQL en el diccionario de entrada")
        
        # Obtener la cadena de conexión
        connection_string = input_data.get("connection_string") or self.connection_string
        if not connection_string:
            # Intentar obtener de la configuración
            db_name = input_data.get("db_name")
            if db_name and db_name in config.database_urls:
                connection_string = config.database_urls[db_name]
            else:
                raise ValueError("Se requiere una cadena de conexión")
        
        # Conectar a la base de datos
        engine = create_engine(connection_string)
        
        # Ejecutar la consulta
        with engine.connect() as connection:
            result = connection.execute(text(query))
            rows = result.fetchall()
            columns = result.keys()
        
        # Convertir a DataFrame de Polars
        df = pl.DataFrame({col: [row[i] for row in rows] for i, col in enumerate(columns)})
        
        # Guardar datos crudos si es necesario
        if self.save_raw:
            file_name = f"{self.name or 'sql'}_{input_data.get('db_name', 'query')}.csv"
            self.output_path.mkdir(parents=True, exist_ok=True)
            df.write_csv(self.output_path / file_name)
        
        metadata = {
            "source": connection_string,
            "query": query,
            "rows": len(df),
            "columns": df.columns,
        }
        
        return TaskResult(df, metadata)


class ExcelExtractor(Task[str, pl.DataFrame]):
    """Extractor Excel corregido basado en diagnóstico."""
    
    def __init__(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        output_path: Optional[Path] = None,
        save_raw: bool = True,
        sheet_name: Union[str, int, None] = None,  # CAMBIO: usar None por defecto
        engine: str = "xlsx2csv",  # CAMBIO: usar xlsx2csv que funciona con sheet_name=None
        infer_schema_length: Optional[int] = 1000,
        **polars_options
    ):
        super().__init__(name, description)
        self.output_path = output_path or config.bronze_dir
        self.save_raw = save_raw
        self.sheet_name = sheet_name
        self.engine = engine
        self.infer_schema_length = infer_schema_length
        self.polars_options = polars_options
    
    def run(self, input_data: str, **kwargs) -> TaskResult[pl.DataFrame]:
        """Extrae datos usando configuración corregida."""
        
        print(f"📄 Procesando: {Path(input_data).name}")
        
        # Configuraciones ordenadas por probabilidad de éxito
        configs = [
            # Configuración principal: xlsx2csv + sheet_name=None (FUNCIONA según diagnóstico)
            {
                "engine": "xlsx2csv",
                "sheet_name": None,
                "description": "📄 xlsx2csv + sheet_name=None"
            },
            # Fallback 1: calamine + sheet_name=None
            {
                "engine": "calamine", 
                "sheet_name": None,
                "description": "🚀 calamine + sheet_name=None"
            },
            # Fallback 2: openpyxl + sheet_name=None
            {
                "engine": "openpyxl",
                "sheet_name": None,
                "description": "🐍 openpyxl + sheet_name=None"
            },
            # Fallback 3: intentar con Hoja1 específica (puede fallar)
            {
                "engine": "xlsx2csv",
                "sheet_name": "Hoja1", 
                "description": "📄 xlsx2csv + Hoja1"
            }
        ]
        
        df = None
        successful_config = None
        
        for config in configs:
            try:
                print(f"  {config['description']}...", end="")
                
                # Preparar parámetros - ELIMINAR dtypes problemático
                read_params = {
                    "source": input_data,
                    "engine": config["engine"],
                    "infer_schema_length": self.infer_schema_length
                }
                
                # Solo agregar sheet_name si no es None
                if config["sheet_name"] is not None:
                    read_params["sheet_name"] = config["sheet_name"]
                
                # NO pasar polars_options que pueden causar el error de dtypes
                # Solo pasar parámetros seguros
                safe_options = {}
                for key, value in self.polars_options.items():
                    if key not in ['dtypes', 'schema_overrides']:  # Evitar parámetros problemáticos
                        safe_options[key] = value
                
                read_params.update(safe_options)
                
                # Leer Excel
                df = pl.read_excel(**read_params)
                
                print(f" ✅ ({len(df)} filas, {len(df.columns)} cols)")
                successful_config = config
                break
                
            except Exception as e:
                error_msg = str(e)[:50]
                print(f" ❌ ({error_msg}...)")
                continue
        
        if df is None:
            raise ValueError(f"No se pudo leer {input_data} con ninguna configuración")
        
        # Post-procesamiento
        df = self._clean_dataframe(df)
        
        # Guardar datos crudos
        if self.save_raw:
            csv_filename = Path(input_data).stem + ".csv"
            csv_content = df.write_csv()
            self.save_raw_data(csv_filename, csv_content)
        
        metadata = {
            "source": input_data,
            "rows": len(df),
            "columns": df.columns,
            "successful_config": successful_config
        }
        
        return TaskResult(df, metadata)
    
    def _clean_dataframe(self, df: pl.DataFrame) -> pl.DataFrame:
        """Limpia el DataFrame."""
        
        # Filtrar filas completamente vacías
        if len(df) > 0:
            df = df.filter(
                pl.fold(
                    acc=False,
                    function=lambda acc, x: acc | x.is_not_null(),
                    exprs=pl.all()
                )
            )
        
        # Limpiar nombres de columnas
        clean_columns = {}
        for col in df.columns:
            clean_name = (str(col).strip()
                         .replace(' ', '_')
                         .replace('\n', '')
                         .replace('\t', '')
                         .replace('(', '')
                         .replace(')', ''))
            clean_columns[col] = clean_name
        
        if clean_columns:
            df = df.rename(clean_columns)
        
        return df
    
    def save_raw_data(self, file_name: str, data: str) -> Path:
        """Guarda datos crudos como CSV."""
        output_file = self.output_path / file_name
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, "w", encoding='utf-8') as f:
            f.write(data)
        
        return output_file


class JSONExtractor(FileExtractor):
    """Extractor para archivos JSON."""
    
    def __init__(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        output_path: Optional[Path] = None,
        save_raw: bool = True,
        data_key: Optional[str] = None,  # Clave específica en el JSON
        **json_options
    ):
        super().__init__(name, description, output_path, save_raw)
        self.data_key = data_key
        self.json_options = json_options
    
    def run(self, input_data: str, **kwargs) -> TaskResult[pl.DataFrame]:
        """Extrae datos de un archivo JSON."""
        is_url = input_data.startswith("http")
        
        if is_url:
            response = requests.get(input_data)
            response.raise_for_status()
            json_data = response.json()
            
            if self.save_raw:
                file_name = input_data.split("/")[-1]
                if not file_name.endswith(".json"):
                    file_name = f"download_{file_name}.json"
                self.save_raw_data(file_name, json_data)
        else:
            # Es una ruta de archivo local
            with open(input_data, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            if self.save_raw and Path(input_data) != self.output_path:
                self.save_raw_data(Path(input_data).name, json_data)
        
        # Extraer datos específicos si se proporciona data_key
        if self.data_key:
            data_to_convert = json_data.get(self.data_key, [])
        else:
            data_to_convert = json_data
        
        # Convertir a DataFrame
        if isinstance(data_to_convert, list):
            df = pl.DataFrame(data_to_convert) if data_to_convert else pl.DataFrame()
        elif isinstance(data_to_convert, dict):
            df = pl.DataFrame([data_to_convert])
        else:
            raise ValueError(f"No se pueden convertir los datos JSON a DataFrame: {type(data_to_convert)}")
        
        metadata = {
            "source": input_data,
            "rows": len(df),
            "columns": df.columns,
            "data_key": self.data_key
        }
        
        return TaskResult(df, metadata)
