using Consultas.Datos.Daos.Abstracciones;
using Consultas.Datos.Entidades;
using Consultas.Datos.Infraestructura;
using System;
using System.Collections.Generic;
using System.Data.SqlClient;
using System.Text;
using System.Threading.Tasks;

namespace Consultas.Datos.Daos.Implementaciones
{
    public class TituloAcademicoDao : ITituloAcademicoDao
    {

        private readonly DatabaseConfiguracion _configuracion;

        public TituloAcademicoDao(
            DatabaseConfiguracion configuracion
            )
        {
            _configuracion = configuracion;
        }


        public async Task EliminarPorDni(string dni)
        {
            var sql = "DELETE FROM TituloAcademico WHERE Dni = @dni";

            using var conexion = new SqlConnection(_configuracion.CadenaConexion);
            using var comando = new SqlCommand(sql, conexion);
            comando.Parameters.AddWithValue("@dni", dni);

            conexion.Open();

            await comando.ExecuteNonQueryAsync();
        }

        public async Task Insertar(TituloAcademico entidad)
        {

            var sql = "INSERT INTO TituloAcademico(Dni, Titulo, Fecha, Institucion) VALUES(@dni, @titulo, @fecha, @institucion) ";

            using var conexion = new SqlConnection(_configuracion.CadenaConexion);
            using var comando = new SqlCommand(sql, conexion);
            comando.Parameters.AddWithValue("@titulo", !string.IsNullOrWhiteSpace(entidad.Titulo) ? entidad.Titulo : (object)DBNull.Value);
            comando.Parameters.AddWithValue("@fecha", !string.IsNullOrWhiteSpace(entidad.Fecha) ? entidad.Fecha : (object)DBNull.Value);
            comando.Parameters.AddWithValue("@institucion", !string.IsNullOrWhiteSpace(entidad.Institucion) ? entidad.Institucion : (object)DBNull.Value);
            comando.Parameters.AddWithValue("@dni", entidad.Dni);


            conexion.Open();

            await comando.ExecuteNonQueryAsync();

        }

    }
}
