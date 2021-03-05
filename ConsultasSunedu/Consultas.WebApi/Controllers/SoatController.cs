using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Consultas.Servicios.Consultas.Soat.Trabajadores.Abstracciones;
using Consultas.WebApi.Infraestructura.Controladores;
using Hangfire;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;

namespace Consultas.WebApi.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class SoatController : ControladorBase
    {

        [HttpGet("IniciarScraping")]
        public string IniciarScraping()
        {
            var idJob = BackgroundJob.Enqueue<ISoatTrabajador>(s =>
                                            s.RealizarTrabajo(JobCancellationToken.Null)
                               );

            return $"suceso con el job {idJob}";
        }
    }
}
