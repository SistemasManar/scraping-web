using System;
using System.Collections.Generic;
using System.Text;
using System.Threading.Tasks;

namespace Consultas.Datos.Daos.Abstracciones
{
    public interface ISuneduDniColaDao
    {

        Task<string> ObtenerSiguiente();

        Task InsertarEnCola(string dni);
    }
}
