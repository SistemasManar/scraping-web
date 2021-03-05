using System;
using System.Collections.Generic;
using System.Text;
using System.Threading.Tasks;
using Hangfire;

namespace Consultas.Servicios.Consultas.Sunedu.Trabajadores.Abstracciones
{

    [Queue("scraping_sunedu")]
    public interface ISuneduTrabajador
    {

        Task RealizarTrabajo( IJobCancellationToken cancellationToken);
    }
}
