using Consultas.Servicios.Consultas.Sunat.Dtos;
using Consultas.Servicios.Infraestructura.Dtos;
using System;
using System.Collections.Generic;
using System.Text;
using System.Threading.Tasks;

namespace Consultas.Servicios.Consultas.Sunat.Servicios.Abstracciones
{
    public interface ISunatServicio
    {
        public Task<OperacionDto<RegistroEmpresaDto>> BuscarEmpresa(PeticionSunatDto peticion);
    }
}
