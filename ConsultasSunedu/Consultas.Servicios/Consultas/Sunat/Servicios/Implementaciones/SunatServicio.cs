using Consultas.Servicios.Consultas.Sunat.Dtos;
using Consultas.Servicios.Consultas.Sunat.Servicios.Abstracciones;
using Consultas.Servicios.Infraestructura.Dtos;
using System;
using System.Collections.Generic;
using System.Text;
using System.Threading.Tasks;
using HtmlAgilityPack;
using RestSharp;
using System.Net;
using System.Linq;
using System.Web;

namespace Consultas.Servicios.Consultas.Sunat.Servicios.Implementaciones
{
    public class SunatServicio : ISunatServicio
    {
        public async Task<OperacionDto<RegistroEmpresaDto>> BuscarEmpresa(PeticionSunatDto peticion)
        {

            var client = new RestClient($"http://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/")
            {
                UserAgent = "Mozilla/5.0 (Linux; Android 5.0.2; SM-G920T Build/LRX22G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.78 Mobile Safari/537.36"
            };

            var codigo = ObtenerCaptcha(client);

            if (string.IsNullOrWhiteSpace(codigo))
            {
                return new OperacionDto<RegistroEmpresaDto>(CodigosOperacionDto.SinAccesoSunat, "No se puede acceder a sunat");
            }

            peticion.CodigoCaptcha = codigo;

            var operacion = await ObtenerEmpresa(client, peticion);

            return operacion;
        }


        private string ObtenerCaptcha(RestClient client)
        {


            var request = new RestRequest("captcha?accion=random", Method.GET);

            var respuesta = client.Execute(request);

            if (respuesta.StatusCode != HttpStatusCode.OK)
            {
                return null;
            }

            var cookieJar = new CookieContainer();
            var sessionCookies = respuesta.Cookies;

            foreach (var cookie in sessionCookies)
            {
                cookieJar.Add(new Cookie(cookie.Name, cookie.Value, cookie.Path, cookie.Domain));
            }


            client.CookieContainer = cookieJar;


            return respuesta.Content;
        }


        private async Task<OperacionDto<RegistroEmpresaDto>> ObtenerEmpresa(RestClient client, PeticionSunatDto peticion)
        {
            var html = ObtenerHtmlGeneral(client, peticion);

            if (string.IsNullOrWhiteSpace(html))
            {
                return new OperacionDto<RegistroEmpresaDto>(CodigosOperacionDto.NoExiste, "No existe ruc");
            }


            var dto = new RegistroEmpresaDto()
            {
                Ruc = peticion.Ruc
            };

            await LlenarDtoDeHtml(dto, html);


            if (!string.IsNullOrEmpty(dto.FechaInscripcion))
            {
                peticion.RazonSocial = dto.Nombre;

                var htmlCantidadTrabajadores = ObtenerHtmlCantidadTrabajadores(client, peticion);
                //var htmlInformacionHistorica = ObtenerHtmlInformacionHistorica(client, peticion);
                var htmlRepresentantesLegales = ObtenerHtmlRepresentantesLegales(client, peticion);

                dto.CantidadTrabajadores = ObtenerCantidadTrabajadoresDeHtml(htmlCantidadTrabajadores);
                dto.Representantes = ObtenerRepresentantesLegales(htmlRepresentantesLegales);
            }

            return new OperacionDto<RegistroEmpresaDto>(dto);
        }

        private string ObtenerHtmlGeneral(RestClient client, PeticionSunatDto peticion)
        {
            var request = new RestRequest($"jcrS00Alias?accion=consPorRuc&nroRuc={peticion.Ruc}&numRnd={peticion.CodigoCaptcha}", Method.GET);
            var resultado = default(string);

            //Encoding encoding = Encoding.UTF8;
            var encoding = Encoding.GetEncoding("ISO-8859-1");
            var response = client.Execute(request);

            if (response.StatusCode == HttpStatusCode.OK)
            {
                resultado = encoding.GetString(response.RawBytes);
            }

            return resultado;
        }

        private string ObtenerHtmlCantidadTrabajadores(RestClient client, PeticionSunatDto peticion)
        {
            var request = new RestRequest($"jcrS00Alias", Method.POST);

            request.AddHeader("Referer", $"http://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/jcrS00Alias?accion=consPorRuc&nroRuc={peticion.Ruc}&numRnd={peticion.CodigoCaptcha}");
            request.AddHeader("Upgrade-Insecure-Requests", "1");
            request.AddHeader("Cache-Control", "max-age=0");
            request.AddHeader("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9");
            request.AddHeader("Accept-Encoding", "gzip, deflate");
            request.AddHeader("Accept-Language", "en-US,en;q=0.9,es-419;q=0.8,es;q=0.7,zh;q=0.6");


            request.AddParameter("submit", "Cantidad de Trabajadores y/o Prestadores de Servicio");
            request.AddParameter("accion", "getCantTrab");
            request.AddParameter("nroRuc", peticion.Ruc);
            request.AddParameter("desRuc", peticion.RazonSocial);

            var resultado = default(string);
            Encoding encoding = Encoding.UTF8;


            var response = client.Execute(request);

            if (response.StatusCode == HttpStatusCode.OK)
            {
                resultado = encoding.GetString(response.RawBytes);
            }

            return resultado;
        }


        //private string ObtenerHtmlInformacionHistorica(RestClient client, PeticionSunatDto peticion)
        //{
        //    var request = new RestRequest($"jcrS00Alias", Method.POST);

        //    request.AddHeader("Referer", $"http://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/jcrS00Alias?accion=consPorRuc&nroRuc={peticion.Ruc}&numRnd={peticion.CodigoCaptcha}");
        //    request.AddHeader("Upgrade-Insecure-Requests", "1");
        //    request.AddHeader("Cache-Control", "max-age=0");
        //    request.AddHeader("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9");
        //    request.AddHeader("Accept-Encoding", "gzip, deflate");
        //    request.AddHeader("Accept-Language", "en-US,en;q=0.9,es-419;q=0.8,es;q=0.7,zh;q=0.6");


        //    request.AddParameter("submit", "(unable to decode value)");
        //    request.AddParameter("accion", "getinfHis");
        //    request.AddParameter("nroRuc", peticion.Ruc);
        //    request.AddParameter("desRuc", peticion.RazonSocial);

        //    var resultado = default(string);
        //    var encoding = Encoding.GetEncoding("ISO-8859-1");

        //    var response = client.Execute(request);

        //    if (response.StatusCode == HttpStatusCode.OK)
        //    {
        //        resultado = encoding.GetString(response.RawBytes);
        //    }

        //    return resultado;
        //}

        private string ObtenerHtmlRepresentantesLegales(RestClient client, PeticionSunatDto peticion)
        {
            var request = new RestRequest($"jcrS00Alias", Method.POST);

            request.AddHeader("Referer", $"http://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/jcrS00Alias?accion=consPorRuc&nroRuc={peticion.Ruc}&numRnd={peticion.CodigoCaptcha}");
            request.AddHeader("Upgrade-Insecure-Requests", "1");
            request.AddHeader("Cache-Control", "max-age=0");
            request.AddHeader("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9");
            request.AddHeader("Accept-Encoding", "gzip, deflate");
            request.AddHeader("Accept-Language", "en-US,en;q=0.9,es-419;q=0.8,es;q=0.7,zh;q=0.6");


            request.AddParameter("accion", "getRepLeg");
            request.AddParameter("nroRuc", peticion.Ruc);
            request.AddParameter("desRuc", peticion.RazonSocial);

            var resultado = default(string);
            var encoding = Encoding.GetEncoding("ISO-8859-1");

            var response = client.Execute(request);

            if (response.StatusCode == HttpStatusCode.OK)
            {
                resultado = encoding.GetString(response.RawBytes);
            }

            return resultado;
        }


        private async Task LlenarDtoDeHtml(RegistroEmpresaDto dto, string html)
        {
            var doc = new HtmlDocument();
            doc.LoadHtml(html);

            var tablas = doc.DocumentNode.Descendants("table").ToList();
            if (tablas.Count < 1)
            {
                return;
            }

            var tabla = tablas.FirstOrDefault();

            var trList = tabla.Descendants().Where(e => e.Name == "tr");

            if (trList == null || trList.Count() == 0)
            {
                return;
            }

            var contador = 0;
            foreach (var tr in trList)
            {
                switch (contador)
                {
                    case 0:
                        var rucPlus = ObtenerResultadoSimpleDeTd(tr, 1);
                        if (!string.IsNullOrWhiteSpace(rucPlus))
                        {
                            var partes = rucPlus.Split(new string[] { "-" }, StringSplitOptions.None);
                            if (partes.Length > 1)
                            {
                                dto.Nombre = !string.IsNullOrWhiteSpace(partes[1]) ? partes[1].Trim() : null;
                            }
                        }
                        break;
                    case 1:
                        dto.TipoContribuyente = ObtenerResultadoSimpleDeTd(tr, 1);
                        break;
                    case 2:
                        dto.NombreComercial = ObtenerResultadoSimpleDeTd(tr, 1);
                        break;
                    case 3:
                        dto.FechaInscripcion = ObtenerResultadoSimpleDeTd(tr, 1);
                        dto.FechaInicioActividades = ObtenerResultadoSimpleDeTd(tr, 3);
                        break;
                    case 4:
                        dto.EstadoContribuyente = ObtenerResultadoSimpleDeTd(tr, 1);
                        break;
                    case 5:
                        dto.CondicionContribuyente = ObtenerResultadoSimpleDeTd(tr, 1);
                        break;
                    case 6:
                        dto.DireccionDomicilioFiscal = ObtenerResultadoSimpleDeTd(tr, 1);
                        break;
                    case 7:
                        dto.SistemaEmisionComprobante = ObtenerResultadoSimpleDeTd(tr, 1);
                        dto.ActividadComercioExterior = ObtenerResultadoSimpleDeTd(tr, 3);
                        break;
                    case 8:
                        dto.SistemaDeContabilidad = ObtenerResultadoSimpleDeTd(tr, 1);
                        break;

                    case 9:
                        var listaActividadesEconomicas = ObtenerListaDeSimpleDeTd(tr, 1);
                        dto.ActividadesEconomicas = listaActividadesEconomicas;
                        break;

                    case 10:
                        var listaComprobantesPago = ObtenerListaDeSimpleDeTd(tr, 1);
                        dto.ComprobantesDePago = listaComprobantesPago;
                        break;
                    case 11:
                        var listaSistemasDeEmisionElectronica = ObtenerListaDeSimpleDeTd(tr, 1);
                        dto.SistemasDeEmisionElectronica = listaSistemasDeEmisionElectronica;
                        break;
                    case 12:
                        dto.EmisorElectronicoDesde = ObtenerResultadoSimpleDeTd(tr, 1);
                        break;
                    case 13:
                        var comprobantes = ObtenerResultadoSimpleDeTd(tr, 1);
                        if (!string.IsNullOrWhiteSpace(comprobantes))
                        {
                            var partes = comprobantes.Split(new string[] { "," }, StringSplitOptions.None);
                            dto.ComprobantesElectronicos.AddRange(partes);
                        }
                        break;
                    case 14:
                        dto.AfiliadoPLEDesde = ObtenerResultadoSimpleDeTd(tr, 1);
                        break;
                    case 15:
                        var listaPadrones = ObtenerListaDeSimpleDeTd(tr, 1);
                        dto.Padrones = listaPadrones;
                        break;
                }

                contador++;
            }

            await LlenarDatosUbigeoDeDireccion(dto);

        }

        private string ObtenerResultadoSimpleDeTd(HtmlNode nodo, int posicion)
        {
            var texto = default(string);
            var tds = nodo.Descendants().Where(e => e.Name == "td").ToList();

            if (posicion < tds.Count)
            {
                texto = tds[posicion].InnerText;
            }

            if (!string.IsNullOrWhiteSpace(texto))
            {
                texto = HttpUtility.HtmlDecode(texto.Trim());
            }

            return texto;
        }

        private List<string> ObtenerListaDeSimpleDeTd(HtmlNode nodo, int posicion)
        {
            var tds = nodo.Descendants().Where(e => e.Name == "td").ToList();

            if (posicion < tds.Count)
            {
                var opciones = tds[posicion].Descendants().Where(e => e.Name == "option").Select(e => e.InnerText).ToList();
                if (opciones == null)
                {
                    return new List<string>();
                }

                var lista = new List<string>();
                foreach (var opcion in opciones)
                {
                    lista.Add(HttpUtility.HtmlDecode(!string.IsNullOrWhiteSpace(opcion) ? opcion.Trim() : ""));
                }

                return lista;
            }


            return new List<string>();
        }

        private async Task LlenarDatosUbigeoDeDireccion(RegistroEmpresaDto dto)
        {
            await Task.Delay(100);
            if (dto == null || string.IsNullOrWhiteSpace(dto.DireccionDomicilioFiscal))
            {
                return;
            }

            var partes = dto.DireccionDomicilioFiscal.Split(new string[] { "-" }, StringSplitOptions.None);

            if (partes.Length < 3)
            {
                return;
            }

            var distrito = !string.IsNullOrWhiteSpace(partes[partes.Length - 1]) ? partes[partes.Length - 1].Trim() : "";
            var provincia = !string.IsNullOrWhiteSpace(partes[partes.Length - 2]) ? partes[partes.Length - 2].Trim() : "";
            var departamentoPorProcesar = !string.IsNullOrWhiteSpace(partes[partes.Length - 3]) ? partes[partes.Length - 3].Trim() : "";

            if (provincia.ToLower().Contains("callao"))
            {
                dto.DistritoDomicilioFiscal = distrito;
                dto.ProvinciaDomicilioFiscal = "CALLAO";
                dto.DepartamentoDomicilioFiscal = "CALLAO";
                return;
            }

            dto.DistritoDomicilioFiscal = distrito;
            dto.ProvinciaDomicilioFiscal = provincia;


            if (string.IsNullOrWhiteSpace(departamentoPorProcesar))
            {
                return;
            }

            var depas = departamentoPorProcesar.Split(new string[] { " " }, StringSplitOptions.None);

            if (partes.Length < 1)
            {
                return;
            }

            var departamento = !string.IsNullOrWhiteSpace(depas[depas.Length - 1]) ? depas[depas.Length - 1].Trim() : "";

            if ("dios".Equals(departamento, StringComparison.OrdinalIgnoreCase))
            {
                departamento = "Madre De Dios";
            }

            if ("libertad".Equals(departamento, StringComparison.OrdinalIgnoreCase))
            {
                departamento = "La Libertad";
            }

            if ("martin".Equals(departamento, StringComparison.OrdinalIgnoreCase))
            {
                departamento = "San Martin";
            }

            dto.DepartamentoDomicilioFiscal = departamento;


            //var ubigeos = await _ubigeoIneiRepositorio.BuscarPorDistritoYProvincia(distrito, provincia);
            //if (ubigeos.Count > 0)
            //{
            //    dto.DepartamentoDomicilioFiscal = ubigeos[0].Departamento?.ToUpper();
            //}

        }

        private List<CantidadTrabajadoresDto> ObtenerCantidadTrabajadoresDeHtml(string html)
        {
            var lista = new List<CantidadTrabajadoresDto>();

            var doc = new HtmlDocument();
            doc.LoadHtml(html);

            var tablas = doc.DocumentNode.Descendants("table").ToList();
            if (tablas.Count < 3)
            {
                return lista;
            }

            var tabla = tablas[2];

            var trList = tabla.Descendants().Where(e => e.Name == "tr");

            if (trList == null || trList.Count() == 0)
            {
                return lista;
            }

            var contador = 0;
            foreach (var tr in trList)
            {
                if (contador >= 2)
                {
                    var cantidadDto = new CantidadTrabajadoresDto()
                    {
                        Periodo = ObtenerResultadoSimpleDeTd(tr, 0),
                        NroTrabajadores = ObtenerResultadoSimpleDeTd(tr, 1),
                        NroPensionistas = ObtenerResultadoSimpleDeTd(tr, 2),
                        NroPrestadoresDeServicio = ObtenerResultadoSimpleDeTd(tr, 3)
                    };

                    if (!string.IsNullOrWhiteSpace(cantidadDto.Periodo))
                    {
                        lista.Add(cantidadDto);
                    }
                }
                contador++;
            }

            return lista;
        }


        private List<RepresentanteLegalDto> ObtenerRepresentantesLegales(string html)
        {
            var lista = new List<RepresentanteLegalDto>();

            var doc = new HtmlDocument();
            doc.LoadHtml(html);

            var tablas = doc.DocumentNode.Descendants("table").ToList();
            if (tablas.Count < 3)
            {
                return lista;
            }

            var tabla = tablas[2];

            var trList = tabla.Descendants().Where(e => e.Name == "tr");

            if (trList == null || trList.Count() == 0)
            {
                return lista;
            }

            var contador = 0;
            foreach (var tr in trList)
            {
                if (contador >= 2)
                {
                    var representante = new RepresentanteLegalDto()
                    {
                        TipoDocumento = ObtenerResultadoSimpleDeTd(tr, 0),
                        NroDocumento = ObtenerResultadoSimpleDeTd(tr, 1),
                        Nombres = ObtenerResultadoSimpleDeTd(tr, 2),
                        Cargo = ObtenerResultadoSimpleDeTd(tr, 3),
                        Desde = ObtenerResultadoSimpleDeTd(tr, 4)
                    };

                    if (!string.IsNullOrWhiteSpace(representante.Nombres))
                    {
                        lista.Add(representante);
                    }
                }
                contador++;
            }

            return lista;
        }
    }
}
