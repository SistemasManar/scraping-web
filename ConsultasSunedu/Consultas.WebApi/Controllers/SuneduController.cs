using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Consultas.Servicios.Consultas.Sunedu.Dtos;
using Consultas.Servicios.Consultas.Sunedu.Servicios.Abstracciones;
using Consultas.Servicios.Consultas.Sunedu.Trabajadores.Abstracciones;
using Consultas.WebApi.Infraestructura.Controladores;
using Hangfire;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;

namespace Consultas.WebApi.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class SuneduController : ControladorBase
    {
        private readonly ISuneduServicio _suneduServicio;
        private readonly SuneduConfiguracionDto _suneduConfiguracion;

        public SuneduController(
            ISuneduServicio suneduServicio,
            SuneduConfiguracionDto suneduConfiguracion
            )
        {
            _suneduServicio = suneduServicio;
            _suneduConfiguracion = suneduConfiguracion;
        }

        [HttpPost("Consulta")]
        public async Task<List<TituloSuneduDto>> ListarTitulos(PeticionTituloSuneduDto peticion)
        {
            peticion.RutaFolderTrabajo = _suneduConfiguracion.RutaFolderTrabajo;
            peticion.RutaTesseract = _suneduConfiguracion.RutaTesseract;
            peticion.UrlSunedu = _suneduConfiguracion.UrlSunedu;
            peticion.UserAgent = _suneduConfiguracion.UserAgent;

            var operacion = await _suneduServicio.ListarTitulos(peticion);

            return ObtenerResultadoOGenerarErrorDeOperacion(operacion);
        }

        [HttpGet("IniciarScraping")]
        public string IniciarScraping()
        {
            var idJob = BackgroundJob.Enqueue<ISuneduTrabajador>(s =>
                                            s.RealizarTrabajo(JobCancellationToken.Null)
                               );

            return $"suceso con el job {idJob}";
        }
    }
}
