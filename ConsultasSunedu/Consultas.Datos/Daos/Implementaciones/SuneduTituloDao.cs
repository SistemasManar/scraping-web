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
    public class SuneduTituloDao : ISuneduTituloDao
    {

        private readonly DatabaseConfiguracion _configuracion;

        public SuneduTituloDao(
            DatabaseConfiguracion configuracion
            )
        {
            _configuracion = configuracion;
        }
        public async Task Actualizar(SuneduTitulo entidad)
        {

            var sql = "UPDATE SuneduTitulo SET Datos = @datos, Creado = @creado, Actualizado = @actualizado WHERE Dni = @dni";

            using var conexion = new SqlConnection(_configuracion.CadenaConexion);
            using var comando = new SqlCommand(sql, conexion);
            comando.Parameters.AddWithValue("@datos", entidad.Datos);
            comando.Parameters.AddWithValue("@creado", entidad.Creado);
            comando.Parameters.AddWithValue("@actualizado", entidad.Actualizado);
            comando.Parameters.AddWithValue("@dni", entidad.Dni);

            conexion.Open();

            await comando.ExecuteNonQueryAsync();

        }

        public async Task Insertar(SuneduTitulo entidad)
        {
            var sql = "INSERT INTO SuneduTitulo(Dni, Datos, Creado, Actualizado) VALUES(@dni, @datos, @creado, @actualizado) ";

            using var conexion = new SqlConnection(_configuracion.CadenaConexion);
            using var comando = new SqlCommand(sql, conexion);
            comando.Parameters.AddWithValue("@datos", entidad.Datos);
            comando.Parameters.AddWithValue("@creado", entidad.Creado);
            comando.Parameters.AddWithValue("@actualizado", entidad.Actualizado);
            comando.Parameters.AddWithValue("@dni", entidad.Dni);

            conexion.Open();

            await comando.ExecuteNonQueryAsync();
        }

        public async Task<SuneduTitulo> Obtener(string dni)
        {
            var entidad = default(SuneduTitulo);

            var sql = "SELECT Dni, Datos, Creado, Actualizado FROM  SuneduTitulo WHERE Dni = @dni";

            using (var conexion = new SqlConnection(_configuracion.CadenaConexion))
            {
                using var comando = new SqlCommand(sql, conexion);
                comando.Parameters.AddWithValue("@dni", dni);

                conexion.Open();
                using var reader = await comando.ExecuteReaderAsync(System.Data.CommandBehavior.CloseConnection);
                while (reader.Read())
                {
                    entidad = new SuneduTitulo()
                    {
                        Dni = reader.GetString(reader.GetOrdinal("Dni")),
                        Datos = reader.GetString(reader.GetOrdinal("Datos")),
                        Creado = reader.GetDateTime(reader.GetOrdinal("Creado")),
                        Actualizado = reader.GetDateTime(reader.GetOrdinal("Actualizado"))
                    };
                }


            }



            return entidad;

        }
    }
}
