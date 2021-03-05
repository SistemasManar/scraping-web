using System;
using System.Collections.Generic;
using System.Text;
using System.Threading.Tasks;
using Hangfire;

namespace Consultas.Servicios.Consultas.Soat.Trabajadores.Abstracciones
{
    [Queue("scraping_apeseg_soat")]
    public interface ISoatTrabajador
    {
        Task RealizarTrabajo(IJobCancellationToken cancellationToken);
    }
}
