using Consultas.Servicios.Consultas.Sunedu.Dtos;
using Consultas.Servicios.Infraestructura.Dtos;
using System;
using System.Collections.Generic;
using System.Text;
using System.Threading.Tasks;

namespace Consultas.Servicios.Consultas.Sunedu.Servicios.Abstracciones
{
    public interface ISuneduServicio
    {
        public Task<OperacionDto<List<TituloSuneduDto>>> ListarTitulos(PeticionTituloSuneduDto peticion);
    }
}
