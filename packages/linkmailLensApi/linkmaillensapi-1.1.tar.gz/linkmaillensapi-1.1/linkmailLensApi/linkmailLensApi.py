import requests
import json
import re
import os
from bs4 import BeautifulSoup
from io import BytesIO
from PIL import Image
import mimetypes

class GoogleLensMatch:
    def __init__(self, image_source, is_url=True):
        """
        Inicializa una búsqueda de Google Lens para una imagen.
        
        Args:
            image_source (str): URL de la imagen o ruta del archivo local
            is_url (bool): True si image_source es URL, False si es ruta local
        """
        self._image_source = image_source
        self._is_url = is_url
        self._simplified_results = None
        self._complete_results = None
        self._vsrid = None
        

        self._process_image()
    
    def _followRedir(self, link2, enlace=None):
        """Seguir la redirección de Google para obtener el vsrid"""
        querystring = {
            "ep": "gsbubu",
            "st": "1751050499056",
            "hl": "es-419",
            "vpw": "1920",
            "vph": "959"
        }
        
        if enlace:
            querystring["url"] = enlace
        
        headers = {
            "host": "lens.google.com",
            "connection": "keep-alive",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "sec-gpc": "1",
            "accept-language": "es-419,es;q=0.9",
            "sec-fetch-site": "same-site",
            "sec-fetch-mode": "navigate",
            "sec-fetch-user": "?1",
            "sec-fetch-dest": "document",
            "sec-ch-ua": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Brave\";v=\"138\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-arch": "\"x86\"",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-ch-ua-platform-version": "\"10.0.0\"",
            "sec-ch-ua-model": "\"\"",
            "sec-ch-ua-bitness": "\"64\"",
            "sec-ch-ua-wow64": "?0",
            "sec-ch-ua-full-version-list": "\"Not)A;Brand\";v=\"8.0.0.0\", \"Chromium\";v=\"138.0.0.0\", \"Brave\";v=\"138.0.0.0\"",
            "referer": "https://www.google.com/",
            "accept-encoding": "gzip, deflate, br, zstd",
            "cookie": "AEC=AVh_V2igNlIPjhAJ4Bm7dPpIZS31Ov-17lbEPTt3JXj7JsnuMnpuyYtcTA; NID=525=AhRVAkLVpUyszXcIbdsDephF2244pq8QoIdVJdLOHLmyl_uOKBNknJGGMh-sXUgrSFkH-5R1rJ2sCLSt-LRYr39AdYtl26JOBXav6ru9KrmmCwv8kZ1AXkA0G7ZlnpgBKNNM3AWCY0MjQugI3Tk70lnBlwtKz-WorUhKYY0jirRlA5HJV53i9Crdy6sWSPXp_CjZlhJJTqqHoiPmwDLzFjvGAQrftDobGX5TeMe1Xo9MyGt1u4V3yPqAL36To6bV6_Y5_JF7"
        }
        
        response = requests.get(link2, headers=headers, params=querystring, allow_redirects=False)
        location = response.headers.get("Location")
        return location

    def _linkStep1(self, link):
        """Pasar el link a Google Lens para iniciar el proceso"""
        url = "https://lens.google.com/v3/upload"
        querystring = {
            "url": link,
            "ep": "gsbubu",
            "st": "1751050499056",
            "authuser": "0",
            "hl": "es-419",
            "vpw": "1920",
            "vph": "959"
        }
        
        headers = {
            "host": "lens.google.com",
            "connection": "keep-alive",
            "sec-ch-ua": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Brave\";v=\"138\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-arch": "\"x86\"",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-ch-ua-platform-version": "\"10.0.0\"",
            "sec-ch-ua-model": "\"\"",
            "sec-ch-ua-bitness": "\"64\"",
            "sec-ch-ua-wow64": "?0",
            "sec-ch-ua-full-version-list": "\"Not)A;Brand\";v=\"8.0.0.0\", \"Chromium\";v=\"138.0.0.0\", \"Brave\";v=\"138.0.0.0\"",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "sec-gpc": "1",
            "accept-language": "es-419,es;q=0.9",
            "sec-fetch-site": "same-site",
            "sec-fetch-mode": "navigate",
            "sec-fetch-user": "?1",
            "sec-fetch-dest": "document",
            "referer": "https://www.google.com/",
            "accept-encoding": "gzip, deflate, br, zstd",
            "cookie": "AEC=AVh_V2igNlIPjhAJ4Bm7dPpIZS31Ov-17lbEPTt3JXj7JsnuMnpuyYtcTA; NID=525=AhRVAkLVpUyszXcIbdsDephF2244pq8QoIdVJdLOHLmyl_uOKBNknJGGMh-sXUgrSFkH-5R1rJ2sCLSt-LRYr39AdYtl26JOBXav6ru9KrmmCwv8kZ1AXkA0G7ZlnpgBKNNM3AWCY0MjQugI3Tk70lnBlwtKz-WorUhKYY0jirRlA5HJV53i9Crdy6sWSPXp_CjZlhJJTqqHoiPmwDLzFjvGAQrftDobGX5TeMe1Xo9MyGt1u4V3yPqAL36To6bV6_Y5_JF7"
        }
        
        response = requests.get(url, headers=headers, params=querystring, allow_redirects=False)
        location = response.headers.get("Location")
        return location
    
    def _upload_image(self, image_path):
        """Sube una imagen directamente a Google Lens mediante POST"""
        url = "https://lens.google.com/v3/upload"
        
        querystring = {
            "ep": "gsbubb",
            "st": "1751056273700",
            "authuser": "0",
            "hl": "es-419",
            "vpw": "1920",
            "vph": "959"
        }
        
        headers = {
            "host": "lens.google.com",
            "connection": "keep-alive",
            "cache-control": "max-age=0",
            "sec-ch-ua": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Brave\";v=\"138\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-arch": "\"x86\"",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-ch-ua-platform-version": "\"10.0.0\"",
            "sec-ch-ua-model": "\"\"",
            "sec-ch-ua-bitness": "\"64\"",
            "sec-ch-ua-wow64": "?0",
            "sec-ch-ua-full-version-list": "\"Not)A;Brand\";v=\"8.0.0.0\", \"Chromium\";v=\"138.0.0.0\", \"Brave\";v=\"138.0.0.0\"",
            "origin": "https://www.google.com",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "sec-gpc": "1",
            "accept-language": "es-419,es;q=0.9",
            "sec-fetch-site": "same-site",
            "sec-fetch-mode": "navigate",
            "sec-fetch-user": "?1",
            "sec-fetch-dest": "document",
            "referer": "https://www.google.com/",
            "accept-encoding": "gzip, deflate, br, zstd",
            "cookie": "AEC=AVh_V2igNlIPjhAJ4Bm7dPpIZS31Ov-17lbEPTt3JXj7JsnuMnpuyYtcTA; NID=525=AhRVAkLVpUyszXcIbdsDephF2244pq8QoIdVJdLOHLmyl_uOKBNknJGGMh-sXUgrSFkH-5R1rJ2sCLSt-LRYr39AdYtl26JOBXav6ru9KrmmCwv8kZ1AXkA0G7ZlnpgBKNNM3AWCY0MjQugI3Tk70lnBlwtKz-WorUhKYY0jirRlA5HJV53i9Crdy6sWSPXp_CjZlhJJTqqHoiPmwDLzFjvGAQrftDobGX5TeMe1Xo9MyGt1u4V3yPqAL36To6bV6_Y5_JF7"
        }
        

        content_type = mimetypes.guess_type(image_path)[0]
        if not content_type:
            content_type = 'image/jpeg'
        

        boundary = "----WebKitFormBoundaryI4YHBA6nbAts73uh"
        headers["content-type"] = f"multipart/form-data; boundary={boundary}"
        

        with open(image_path, 'rb') as image_file:
            file_content = image_file.read()
        

        body = b''
        body += f'--{boundary}\r\n'.encode()
        body += f'Content-Disposition: form-data; name="encoded_image"; filename="{os.path.basename(image_path)}"\r\n'.encode()
        body += f'Content-Type: {content_type}\r\n\r\n'.encode()
        body += file_content
        body += f'\r\n--{boundary}--\r\n'.encode()
        

        response = requests.post(url, data=body, headers=headers, params=querystring, allow_redirects=False)
        

        location = response.headers.get("Location")
        
        
        return location

    def _extract_vsrid(self, redirect_url):
        """Extraer el parámetro vsrid de la URL redirigida"""
        vsrid_match = re.search(r'vsrid=([^&]+)', redirect_url)
        if vsrid_match:
            return vsrid_match.group(1)
        return None

    def _element_to_dict(self, element):
        """Convertir un elemento HTML a formato de diccionario para JSON"""
        if element.name is None:
            text = element.string
            if text and text.strip():
                return text.strip()
            return None
        
        result = {"tag": element.name}
        
        if element.attrs:
            result["attributes"] = {}
            for key, value in element.attrs.items():
                result["attributes"][key] = value
        
        children = []
        for child in element.children:
            child_dict = self._element_to_dict(child)
            if child_dict:
                children.append(child_dict)
        
        if children:
            result["children"] = children
            
        return result

    def _extract_ulsxyf_divs_to_json(self, response_text):
        """Extraer divs con clase ULSxyf del HTML y convertirlos a JSON"""
        try:
            result_divs = []
            
            soup = BeautifulSoup(response_text, 'html.parser')
            ulsxyf_divs = soup.find_all('div', class_='ULSxyf')
            
            if ulsxyf_divs:
                for div in ulsxyf_divs:
                    result_divs.append(self._element_to_dict(div))
            else:
                div_pattern = re.compile(r'<div\s+class="ULSxyf"[^>]*>(.*?)</div>\s*</div>\s*</div>', re.DOTALL)
                matches = div_pattern.finditer(response_text)
                
                for match in matches:
                    div_html = f'<div class="ULSxyf">{match.group(1)}</div>'
                    div_soup = BeautifulSoup(div_html, 'html.parser')
                    result_divs.append(self._element_to_dict(div_soup.div))
            
            if not result_divs:
                return {"error": "No se encontraron divs con clase ULSxyf"}
            
            return result_divs
        
        except Exception as e:
            return {"error": f"Error al procesar el HTML: {str(e)}"}

    def _extract_with_regex_and_bs4(self, response_text):
        """Enfoque alternativo usando regex para extraer primero los bloques grandes"""
        result_divs = []
        
        pattern = re.compile(r'(<div\s+class="ULSxyf".*?</div>\s*</div>\s*</div>)', re.DOTALL)
        matches = pattern.findall(response_text)
        
        for match in matches:
            try:
                soup = BeautifulSoup(match, 'html.parser')
                div = soup.find('div', class_='ULSxyf')
                if div:
                    result_divs.append(self._element_to_dict(div))
            except Exception as e:
                continue
        
        if not result_divs:
            try:
                rso_pattern = re.compile(r'<div\s+class="dURPMd"[^>]*id="rso"[^>]*>(.*?)</div>\s*</div>\s*</div>', re.DOTALL)
                rso_match = rso_pattern.search(response_text)
                
                if rso_match:
                    soup = BeautifulSoup(f"<div>{rso_match.group(1)}</div>", 'html.parser')
                    ulsxyf_divs = soup.find_all('div', class_='ULSxyf')
                    
                    for div in ulsxyf_divs:
                        result_divs.append(self._element_to_dict(div))
            except:
                pass
        
        if not result_divs:
            return {"error": "No se encontraron divs con clase ULSxyf"}
        
        return result_divs

    def _extract_specific_info(self, result_div):
        """Extraer información específica de cada resultado"""
        extracted_info = {
            "title": None,
            "url": None,
            "ping": None,
            "resolution": None,
            "date": None,
            "source_icon": None
        }
        
        def search_node(node, path=""):
            if isinstance(node, str):
                if "ZhosBf" in path:
                    extracted_info["title"] = node
                elif "style-white-space:nowrap" in path:
                    if "x" in node and any(c.isdigit() for c in node):
                        extracted_info["resolution"] = node
                    elif "hace" in node or "año" in node or "mes" in node or "día" in node:
                        extracted_info["date"] = node
            
            elif isinstance(node, dict):
                if "attributes" in node and "href" in node["attributes"]:
                    extracted_info["url"] = node["attributes"]["href"]
                
                if "attributes" in node and "ping" in node["attributes"]:
                    extracted_info["ping"] = node["attributes"]["ping"]
                
                if ("attributes" in node and "src" in node["attributes"] and 
                    isinstance(node["attributes"]["src"], str) and 
                    node["attributes"]["src"].startswith("data:image/png;base64,")):
                    if "attributes" in node and "class" in node["attributes"] and "XNo5Ab" in node["attributes"]["class"]:
                        extracted_info["source_icon"] = node["attributes"]["src"]
                
                new_path = path
                if "attributes" in node and "class" in node["attributes"]:
                    classes = node["attributes"]["class"]
                    if isinstance(classes, list):
                        new_path = path + "-" + "-".join(classes)
                    else:
                        new_path = path + "-" + classes
                
                if "attributes" in node and "style" in node["attributes"]:
                    new_path = new_path + "-" + node["attributes"]["style"]
                
                if "children" in node and node["children"]:
                    for child in node["children"]:
                        search_node(child, new_path)
        
        search_node(result_div)
        
        return extracted_info

    def _process_image(self):
        """Procesa una imagen con Google Lens y extrae los resultados"""
        try:

            if self._is_url:

                redir = self._linkStep1(self._image_source)
                

                redirect_url = self._followRedir(redir, self._image_source)
            else:

                redirect_url = self._upload_image(self._image_source)
                

            self._vsrid = self._extract_vsrid(redirect_url)

            
            if not self._vsrid:
                self._simplified_results = {"error": "No se pudo obtener el vsrid"}
                return
            

            url = "https://www.google.com/search"
            
            querystring = {
                "sca_esv": "6d0ad94c53cfdd66",
                "lns_surface": "26",
                "hl": "es-419",
                "q": "",
                "vsrid": self._vsrid,
                "vsint": "CAIqDAoCCAcSAggKGAEgATojChYNAAAAPxUAAAA_HQAAgD8lAACAPzABEOgHGLIEJQAAgD8",
                "lns_mode": "un",
                "source": "lns.web.gsbubu",
                "vsdim": "1000,562",
                "gsessionid": "iZi76igN_Z6mZHN7e5vQmFD1sMe1U6YWnDuiS7lhCrupVVCEgngiFA",
                "lsessionid": "q4L2_1k5LHVHnmG2jyxtBxeMM0vHAkT1RLzibeDrDeanuKSf-fJcqQ",
                "udm": "48",
                "fbs": "AIIjpHyDuDaSWI128HHkGNYTlSjb1_oTF4ZmPtdzykbpzfBSpb5sLBh_s3SW7YmAyVMS_U2h5ElB",
                "sa": "X",
                "ved": "2ahUKEwi6teXprZKOAxXnVTABHSRJGUAQs6gLKAF6BAgPEAE",
                "biw": "1920",
                "bih": "959",
                "dpr": "1"
            }
            
            headers = {
                "host": "www.google.com",
                "connection": "keep-alive",
                "cache-control": "max-age=0",
                "sec-ch-ua": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Brave\";v=\"138\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-arch": "\"x86\"",
                "sec-ch-ua-platform": "\"Windows\"",
                "sec-ch-ua-platform-version": "\"10.0.0\"",
                "sec-ch-ua-model": "\"\"",
                "sec-ch-ua-bitness": "\"64\"",
                "sec-ch-ua-wow64": "?0",
                "sec-ch-ua-full-version-list": "\"Not)A;Brand\";v=\"8.0.0.0\", \"Chromium\";v=\"138.0.0.0\", \"Brave\";v=\"138.0.0.0\"",
                "upgrade-insecure-requests": "1",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "sec-gpc": "1",
                "accept-language": "es-419,es;q=0.9",
                "sec-fetch-site": "same-origin",
                "sec-fetch-mode": "navigate",
                "sec-fetch-user": "?1",
                "sec-fetch-dest": "document",
                "referer": "https://www.google.com/",
                "accept-encoding": "gzip, deflate, br, zstd",
                "cookie": "AEC=AVh_V2igNlIPjhAJ4Bm7dPpIZS31Ov-17lbEPTt3JXj7JsnuMnpuyYtcTA; NID=525=AhRVAkLVpUyszXcIbdsDephF2244pq8QoIdVJdLOHLmyl_uOKBNknJGGMh-sXUgrSFkH-5R1rJ2sCLSt-LRYr39AdYtl26JOBXav6ru9KrmmCwv8kZ1AXkA0G7ZlnpgBKNNM3AWCY0MjQugI3Tk70lnBlwtKz-WorUhKYY0jirRlA5HJV53i9Crdy6sWSPXp_CjZlhJJTqqHoiPmwDLzFjvGAQrftDobGX5TeMe1Xo9MyGt1u4V3yPqAL36To6bV6_Y5_JF7; DV=A-WYawhQJiUacJwiBMaOV25ZU40uexk"
            }
            

            response = requests.get(url, headers=headers, params=querystring)
            

            complete_results = self._extract_with_regex_and_bs4(response.text)
            
            if "error" in complete_results:
                complete_results = self._extract_ulsxyf_divs_to_json(response.text)
            

            self._complete_results = complete_results
            
            simplified_results = []
            for result in complete_results:
                simplified_result = self._extract_specific_info(result)
                if simplified_result["url"]:
                    simplified_results.append(simplified_result)
            
            self._simplified_results = simplified_results
        
        except Exception as e:
            self._simplified_results = {"error": f"Error al procesar la imagen: {str(e)}"}
            self._complete_results = {"error": f"Error al procesar la imagen: {str(e)}"}
    
    @property
    def response(self):
     """
    Devuelve los resultados simplificados y guarda en archivo JSON
    """
   
     current_dir = os.getcwd()
    
   
     file_path = os.path.join(current_dir, 'googleLensResults.json')
    
   
     with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(self._simplified_results, json_file, ensure_ascii=False, indent=2)
    
     return self._simplified_results

    
    @property
    def realResponse(self):
     """
    Devuelve los resultados completos y guarda en archivo JSON
    """
  
     current_dir = os.getcwd()
    
    
     file_path = os.path.join(current_dir, 'googleLensRealResponse.json')
    
   
     with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(self._complete_results, json_file, ensure_ascii=False, indent=2)
    
     return self._complete_results
    
    @property
    def pages(self):
        """
        Devuelve solo las URLs de todos los matches
        """
        if not self._simplified_results or isinstance(self._simplified_results, dict):
            return []
        
        return [match.get("url") for match in self._simplified_results if match.get("url")]
    
    def __str__(self):
        """
        Representación en cadena de texto del objeto
        """
        if isinstance(self._simplified_results, dict) and "error" in self._simplified_results:
            return f"Error: {self._simplified_results['error']}"
        
        num_matches = len(self._simplified_results) if self._simplified_results else 0
        source_type = "URL" if self._is_url else "archivo local"
        return f"GoogleLensMatch: {num_matches} resultados encontrados para {source_type}"

def lenSearchUrl(image_url):
    """
    Función auxiliar para buscar con una URL de imagen
    
    Args:
        image_url (str): URL de la imagen a buscar
        
    Returns:
        GoogleLensMatch: Objeto con los resultados de la búsqueda
    """
    return GoogleLensMatch(image_url, is_url=True)

def lenSearchImg(image_path):
    """
    Función auxiliar para buscar con una imagen local
    
    Args:
        image_path (str): Ruta del archivo de imagen local
        
    Returns:
        GoogleLensMatch: Objeto con los resultados de la búsqueda
    """
    return GoogleLensMatch(image_path, is_url=False)