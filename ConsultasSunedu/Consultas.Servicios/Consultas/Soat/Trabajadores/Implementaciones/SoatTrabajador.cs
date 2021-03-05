using Consultas.Datos.Daos.Abstracciones;
using Consultas.Datos.Entidades;
using Consultas.Servicios.Consultas.Soat.Dtos;
using Consultas.Servicios.Consultas.Soat.Trabajadores.Abstracciones;
using Hangfire;
using Newtonsoft.Json;
using RestSharp;
using System;
using System.Collections.Generic;
using System.Net;
using System.Text;
using System.Threading.Tasks;

namespace Consultas.Servicios.Consultas.Soat.Trabajadores.Implementaciones
{
    public class SoatTrabajador : ISoatTrabajador
    {
        private readonly ISoatDao _soatDao;

        public SoatTrabajador(ISoatDao soatDao)
        {
            _soatDao = soatDao;
        }

        public async Task RealizarTrabajo(IJobCancellationToken cancellationToken)
        {
            while (true)
            {
                var hora = DateTime.Now.Hour;
                var delay = 20000;

                if (hora >= 6 && hora < 23)
                {
                    delay = 10000;
                }

                try
                {
                    await RealizarScraping();
                }
                catch { }

                cancellationToken.ThrowIfCancellationRequested();
                await Task.Delay(delay);
            }
        }
        private async Task RealizarScraping()
        {
            var placaActual = await _soatDao.ObtenerPlacaParaScraping();
            if (string.IsNullOrWhiteSpace(placaActual))
            {
                return;
            }


            var restClient = new RestClient("http://161.132.211.214/Scrap/api/SimpleSoat/Buscar");
            //restClient.Proxy = new WebProxy("");
            //restClient.Proxy.Credentials = new NetworkCredential("", "");
 
            var restRequest = new RestRequest()
            {
                Method = Method.POST
            };

            restRequest.AddHeader("Content-Type", "application/json");
            restRequest.AddJsonBody(new { placa = placaActual, clave = "KjsdiaiuJHJPIOHN112lasdjpaosdmapkskao2341121312aasdasd" });

            restRequest.Timeout = 1000 * 60 * 10;
            var response = restClient.Execute(restRequest);

            if (response.StatusCode != HttpStatusCode.OK)
            {
                return;
            }

            var dto = JsonConvert.DeserializeObject<RegistroSoatDto>(response.Content);

            if (dto == null)
            {
                return;
            }

            var entidad = new Datos.Entidades.Soat()
            {
                ClaseVehiculo = dto.ClaseVehiculo,
                CodigoSbsAseguradora = dto.CodigoSbsAseguradora,
                CodigoUnicoPoliza = dto.CodigoUnicoPoliza,
                Compania = dto.Compania,
                Contratante = dto.Contratante,
                Estado = dto.Estado,
                FechaControlPolicial = dto.FechaControlPolicial,
                FechaCreacion = dto.FechaCreacion,
                FechaFin = dto.FechaFin,
                FechaInicio = dto.FechaInicio,
                NumeroAseguradora = dto.NumeroAseguradora,
                NumeroPoliza = dto.NumeroPoliza,
                Placa = dto.Placa,
                SerieChasis = dto.SerieChasis,
                SerieMotor = dto.SerieMotor,
                TipoCertificado = dto.TipoCertificado,
                Ubigeo = dto.Ubigeo,
                UsoVehiculo = dto.UsoVehiculo

            };

            await _soatDao.InsertarOActualizar(entidad);
        }

    }
}
