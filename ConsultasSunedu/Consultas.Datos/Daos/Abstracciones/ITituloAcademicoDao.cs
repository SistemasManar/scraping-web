using Consultas.Datos.Entidades;
using System;
using System.Collections.Generic;
using System.Text;
using System.Threading.Tasks;

namespace Consultas.Datos.Daos.Abstracciones
{
    public interface ITituloAcademicoDao
    {

        Task EliminarPorDni(string dni);

        Task Insertar(TituloAcademico entidad);

    }
}
