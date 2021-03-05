using System;
using System.Collections.Generic;
using System.Text;
using System.Threading.Tasks;
using Hangfire;

namespace Consultas.Servicios.Consultas.Sunat.Trabajadores.Abstracciones
{
    [Queue("scraping_sunat_empresa")]
    public interface ISunatTrabajador
    {

        Task RealizarTrabajo(IJobCancellationToken cancellationToken);
    }
}
