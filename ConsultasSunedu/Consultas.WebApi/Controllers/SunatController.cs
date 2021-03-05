using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Consultas.Servicios.Consultas.Sunat.Dtos;
using Consultas.Servicios.Consultas.Sunat.Servicios.Abstracciones;
using Consultas.Servicios.Consultas.Sunat.Trabajadores.Abstracciones;
using Consultas.WebApi.Infraestructura.Controladores;
using Hangfire;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;

namespace Consultas.WebApi.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class SunatController : ControladorBase
    {

        private readonly ISunatServicio _sunatServicio;

        public SunatController(
            ISunatServicio sunatServicio
            )
        {
            _sunatServicio = sunatServicio;
        }

        [HttpPost("Consulta")]
        public async Task<RegistroEmpresaDto> Consulta(PeticionSunatDto peticion)
        {

            var operacion = await _sunatServicio.BuscarEmpresa(peticion);

            return ObtenerResultadoOGenerarErrorDeOperacion(operacion);
        }

        [HttpGet("IniciarScraping")]
        public string IniciarScraping()
        {
            var idJob = BackgroundJob.Enqueue<ISunatTrabajador>(s =>
                                            s.RealizarTrabajo(JobCancellationToken.Null)
                               );

            return $"suceso con el job {idJob}";
        }

    }
}
