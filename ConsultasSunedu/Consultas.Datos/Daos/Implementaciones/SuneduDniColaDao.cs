using Consultas.Datos.Daos.Abstracciones;
using Consultas.Datos.Infraestructura;
using System;
using System.Collections.Generic;
using System.Data.SqlClient;
using System.Text;
using System.Threading.Tasks;

namespace Consultas.Datos.Daos.Implementaciones
{
    public class SuneduDniColaDao : ISuneduDniColaDao
    {

        private readonly DatabaseConfiguracion _configuracion;

        public SuneduDniColaDao(
            DatabaseConfiguracion configuracion
            )
        {
            _configuracion = configuracion;
        }


        public async Task InsertarEnCola(string dni)
        {
            var sql = "INSERT INTO SuneduDniCola(Dni) VALUES(@dni) ";

            using var conexion = new SqlConnection(_configuracion.CadenaConexion);
            using var comando = new SqlCommand(sql, conexion);
            comando.Parameters.AddWithValue("@dni", dni);

            conexion.Open();

            await comando.ExecuteNonQueryAsync();
        }

        public async Task<string> ObtenerSiguiente()
        {

            var dni = default(string);

            using (var conexion = new SqlConnection(_configuracion.CadenaConexion))
            {
                using var comando = new SqlCommand("usp_obtener_dni_de_cola_sunedu", conexion);
                comando.CommandType = System.Data.CommandType.StoredProcedure;

                conexion.Open();
                using var reader = await comando.ExecuteReaderAsync(System.Data.CommandBehavior.CloseConnection);
                while (reader.Read())
                {
                    dni = !reader.IsDBNull(reader.GetOrdinal("Dni")) ? reader.GetString(reader.GetOrdinal("Dni")) : null;
                }


            }



            return dni;

        }
    }
}
