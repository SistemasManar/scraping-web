using Consultas.Datos.Daos.Abstracciones;
using Consultas.Datos.Entidades;
using Consultas.Servicios.Consultas.Sunedu.Dtos;
using Consultas.Servicios.Consultas.Sunedu.Servicios.Abstracciones;
using Consultas.Servicios.Infraestructura.Dtos;
using HtmlAgilityPack;
using Newtonsoft.Json;
using RestSharp;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.Drawing.Imaging;
using System.IO;
using System.Linq;
using System.Net;
using System.Text;
using System.Threading.Tasks;
using System.Web;

namespace Consultas.Servicios.Consultas.Sunedu.Servicios.Implementaciones
{
    public class SuneduServicio : ISuneduServicio
    {

        private readonly ISuneduTituloDao _suneduTituloDao;


        public SuneduServicio(
            ISuneduTituloDao suneduTituloDao
            )
        {
            _suneduTituloDao = suneduTituloDao;
        }

        public async Task<OperacionDto<List<TituloSuneduDto>>> ListarTitulos(PeticionTituloSuneduDto peticion)
        {
            var resultados = await ObtenerDeCache(peticion.Dni);
            bool fueDeCache = true;

            if (string.IsNullOrWhiteSpace(resultados))
            {
                resultados = ObtenerResultado(peticion);
                fueDeCache = false;
            }


            if (string.IsNullOrWhiteSpace(resultados))
            {
                return new OperacionDto<List<TituloSuneduDto>>(CodigosOperacionDto.NoExiste, "No se encontró información");
            }

            if (!string.IsNullOrWhiteSpace(resultados) && resultados.ToLower().Contains("captcha es incorrecto".ToLower()))
            {
                return new OperacionDto<List<TituloSuneduDto>>(CodigosOperacionDto.CaptchaIncorrecto, "No se puede acceder a la info");
            }

            var datoGuardar = new StringBuilder(resultados);


            resultados = resultados.Replace("\t", "");
            resultados = resultados.Replace("<b>", "");
            resultados = resultados.Replace(@"\u00d1", "Ñ");
            resultados = resultados.Replace(@"\u00c1", "Á");
            resultados = resultados.Replace(@"\u00c9", "É");
            resultados = resultados.Replace(@"\u00cd", "Í");
            resultados = resultados.Replace(@"\u00d3", "Ó");
            resultados = resultados.Replace(@"\u00da", "Ú");

            resultados = resultados.Substring(1, resultados.Length - 2).Replace("\\", "");


            var infoScraper = JsonConvert.DeserializeObject<List<TituloScraperDto>>(resultados);
            if (infoScraper == null)
            {
                return new OperacionDto<List<TituloSuneduDto>>(CodigosOperacionDto.NoExiste, "No se encontró información");
            }

            if (!fueDeCache)
            {
                var entidad = await _suneduTituloDao.Obtener(peticion.Dni);
                if (entidad == null)
                {
                    entidad = new SuneduTitulo()
                    {
                        Dni = peticion.Dni,
                        Datos = datoGuardar.ToString()
                    };
                    await _suneduTituloDao.Insertar(entidad);
                }
                else
                {
                    entidad.Datos = datoGuardar.ToString();
                    entidad.Actualizado = DateTime.UtcNow;
                    await _suneduTituloDao.Actualizar(entidad);
                }

            }


            return new OperacionDto<List<TituloSuneduDto>>(infoScraper.Select(e => new TituloSuneduDto()
            {
                FechaDiploma = e.DiplFec,
                Institucion = e.Univ,
                NombreCompleto = e.Nombre,
                Titulo = e.TituloRev

            }).ToList());

        }

        private string ObtenerResultado(PeticionTituloSuneduDto peticion)
        {
            var client = new RestClient(peticion.UrlSunedu)
            {
                UserAgent = peticion.UserAgent
            };

            var token = ObtenerToken(client);

            if (string.IsNullOrWhiteSpace(token))
            {
                return null;
            }


            var captcha = ObtenerCaptcha(client, peticion);

            if (string.IsNullOrWhiteSpace(captcha))
            {
                return null;
            }

            var resultados = ObtenerDatosResultados(client, peticion, captcha, token);

            return resultados;
        }

        private string ObtenerToken(RestClient client)
        {
            var htmlPagina = ObtenerPaginaHtml(client);

            if (string.IsNullOrWhiteSpace(htmlPagina))
            {
                return null;
            }


            var doc = new HtmlDocument();
            doc.LoadHtml(htmlPagina);

            var htmlNode = doc.GetElementbyId("token");

            if (htmlNode == null)
            {
                return null;
            }
            return htmlNode.Attributes["value"].Value;
        }


        private string ObtenerPaginaHtml(RestClient client)
        {

            string resultado = null;
            var peticion = new RestRequest(Method.GET);

            var respuesta = client.Execute(peticion);

            var encoding = Encoding.GetEncoding("ISO-8859-1");


            if (respuesta.StatusCode == HttpStatusCode.OK)
            {
                resultado = encoding.GetString(respuesta.RawBytes);
            }

            var cookieJar = new CookieContainer();
            var sessionCookies = respuesta.Cookies;

            foreach (var cookie in sessionCookies)
            {
                cookieJar.Add(new Cookie(cookie.Name, cookie.Value, cookie.Path, cookie.Domain));
            }


            client.CookieContainer = cookieJar;

            return resultado;
        }

        private string ObtenerRutaFotoCaptcha(RestClient client, PeticionTituloSuneduDto peticion)
        {

            var ruta = $@"{peticion.RutaFolderTrabajo}{Guid.NewGuid()}.png";

            Random r = new Random();
            int rInt = r.Next(400, 997);

            if (System.IO.File.Exists(ruta))
            {
                System.IO.File.Delete(ruta);
            }

            var request = new RestRequest($"simplecaptcha?date={rInt}");
            byte[] response = client.DownloadData(request);

            if (response == null)
            {
                return null;
            }


            System.IO.File.WriteAllBytes(ruta, response);

            return ruta;
        }

        private string ObtenerCaptcha(RestClient client, PeticionTituloSuneduDto peticion)
        {
            var ruta = ObtenerRutaFotoCaptcha(client, peticion);

            if (string.IsNullOrWhiteSpace(ruta))
            {
                return null;
            }

            var captcha = ObtenerCodigo(ruta, peticion);

            return captcha;

        }

        private string ObtenerCodigo(string rutaImagen, PeticionTituloSuneduDto peticion)
        {
            var rutaFinal = $@"{peticion.RutaFolderTrabajo}{Path.GetFileNameWithoutExtension(rutaImagen)}";
            var comando = $@"""{rutaImagen}"" ""{rutaFinal}""";

            var procesoInformacion = new ProcessStartInfo(peticion.RutaTesseract)
            {
                Arguments = comando,
                UseShellExecute = false,
                CreateNoWindow = true
                //,
                //RedirectStandardOutput = true,
                //RedirectStandardError = true
            };

            var cmd = Process.Start(procesoInformacion);
            cmd.WaitForExit();

            var texto = System.IO.File.ReadAllText($@"{rutaFinal}.txt");
            var textoLimpio = LimpiarTexto(texto);
            return textoLimpio;
        }


        private string LimpiarTexto(string texto)
        {
            if (string.IsNullOrEmpty(texto))
            {
                return texto;
            }

            var resultado = texto.Replace("", "");
            resultado = resultado.Replace("", "");
            resultado = resultado.Replace(@"\r\n", "");
            resultado = resultado.Replace(@"\n", "");
            resultado = resultado.Replace(@"\r", "");
            resultado = resultado.Replace(@"_", "");
            resultado = resultado.Replace(@"-", "");
            resultado = resultado.Replace(@"?", "");
            resultado = resultado.Replace(@"=", "");
            resultado = resultado.Replace(@":", "");
            resultado = resultado.Replace(@".", "");
            resultado = resultado.Replace(@"*", "");
            resultado = resultado.Replace(@"\", "");
            resultado = resultado.Replace(@"$", "s");
            resultado = resultado.Replace(@"ceP", "cP");

            resultado = resultado.Trim();

            if (resultado.Length > 5)
            {
                resultado = resultado.Substring(0, 5);
            }


            return resultado;
        }


        private string ObtenerDatosResultados(RestClient client, PeticionTituloSuneduDto peticion, string captcha, string token)
        {

            var resultado = default(string);
            var request = new RestRequest($"consulta", Method.POST);

            request.AddHeader("Referer", peticion.UrlSunedu);
            request.AddHeader("Upgrade-Insecure-Requests", "1");
            request.AddHeader("Cache-Control", "max-age=0");
            request.AddHeader("Accept", "application/json, text/javascript, */*; q=0.01");
            request.AddHeader("Accept-Encoding", "gzip, deflate, br");
            request.AddHeader("Accept-Language", "en-US,en;q=0.9,es-419;q=0.8,es;q=0.7,zh;q=0.6");


            request.AddParameter("doc", peticion.Dni);
            request.AddParameter("opcion", "PUB");
            request.AddParameter("_token", token);
            request.AddParameter("icono", "");
            request.AddParameter("captcha", captcha);

            var response = client.Execute(request);

            if (response.StatusCode == HttpStatusCode.OK)
            {
                resultado = response.Content;
            }

            return resultado;

        }

        private async Task<string> ObtenerDeCache(string dni)
        {
            var entidad = await _suneduTituloDao.Obtener(dni);

            if (entidad == null)
            {
                return null;
            }

            if ((DateTime.UtcNow - entidad.Actualizado).TotalDays > 30)
            {
                return null;
            }
            return entidad.Datos;
        }

    }
}
