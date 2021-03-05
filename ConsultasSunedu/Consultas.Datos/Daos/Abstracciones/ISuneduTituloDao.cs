using Consultas.Datos.Entidades;
using System;
using System.Collections.Generic;
using System.Text;
using System.Threading.Tasks;

namespace Consultas.Datos.Daos.Abstracciones
{
    public interface ISuneduTituloDao
    {
        Task Actualizar(SuneduTitulo entidad);

        Task Insertar(SuneduTitulo entidad);

        Task<SuneduTitulo> Obtener(string dni);

    }
}
