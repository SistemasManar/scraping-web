using Consultas.Datos.Daos.Abstracciones;
using Consultas.Datos.Entidades;
using Consultas.Datos.Infraestructura;
using System;
using System.Collections.Generic;
using System.Data;
using System.Data.SqlClient;
using System.Text;
using System.Threading.Tasks;

namespace Consultas.Datos.Daos.Implementaciones
{
    public class SoatDao : ISoatDao
    {

        private readonly DatabaseConfiguracion _configuracion;

        public SoatDao(
            DatabaseConfiguracion configuracion
            )
        {
            _configuracion = configuracion;
        }

        public async Task InsertarOActualizar(Soat entidad)
        {
            using var conexion = new SqlConnection(_configuracion.CadenaConexion);
            using var comando = new SqlCommand("up_insertar_o_actualizar_soat", conexion);
            comando.CommandType = CommandType.StoredProcedure;
            comando.Parameters.AddWithValue("@Placa", entidad.Placa);
            comando.Parameters.AddWithValue("@Compania", !string.IsNullOrWhiteSpace(entidad.Compania) ? entidad.Compania : (object)DBNull.Value);
            comando.Parameters.AddWithValue("@Inicio", !string.IsNullOrWhiteSpace(entidad.FechaInicio) ? entidad.FechaInicio : (object)DBNull.Value);
            comando.Parameters.AddWithValue("@Fin", !string.IsNullOrWhiteSpace(entidad.FechaFin) ? entidad.FechaFin : (object)DBNull.Value);
            comando.Parameters.AddWithValue("@NumeroPoliza", !string.IsNullOrWhiteSpace(entidad.NumeroPoliza) ? entidad.NumeroPoliza : (object)DBNull.Value);
            comando.Parameters.AddWithValue("@UsoVehiculo", !string.IsNullOrWhiteSpace(entidad.UsoVehiculo) ? entidad.UsoVehiculo : (object)DBNull.Value);
            comando.Parameters.AddWithValue("@ClaseVehiculo", !string.IsNullOrWhiteSpace(entidad.ClaseVehiculo) ? entidad.ClaseVehiculo : (object)DBNull.Value);
            comando.Parameters.AddWithValue("@Estado", !string.IsNullOrWhiteSpace(entidad.Estado) ? entidad.Estado : (object)DBNull.Value);
            comando.Parameters.AddWithValue("@CodigoUnicoPoliza", !string.IsNullOrWhiteSpace(entidad.CodigoUnicoPoliza) ? entidad.CodigoUnicoPoliza : (object)DBNull.Value);
            comando.Parameters.AddWithValue("@CodigoSbsAseguradora", !string.IsNullOrWhiteSpace(entidad.CodigoSbsAseguradora) ? entidad.CodigoSbsAseguradora : (object)DBNull.Value);
            comando.Parameters.AddWithValue("@FechaControlPolicial", !string.IsNullOrWhiteSpace(entidad.FechaControlPolicial) ? entidad.FechaControlPolicial : (object)DBNull.Value);
            comando.Parameters.AddWithValue("@Contratante", !string.IsNullOrWhiteSpace(entidad.Contratante) ? entidad.Contratante : (object)DBNull.Value);
            comando.Parameters.AddWithValue("@Ubigeo", !string.IsNullOrWhiteSpace(entidad.Ubigeo) ? entidad.Ubigeo : (object)DBNull.Value);
            comando.Parameters.AddWithValue("@SerieMotor", !string.IsNullOrWhiteSpace(entidad.SerieMotor) ? entidad.SerieMotor : (object)DBNull.Value);
            comando.Parameters.AddWithValue("@SerieChasis", !string.IsNullOrWhiteSpace(entidad.SerieChasis) ? entidad.SerieChasis : (object)DBNull.Value);
            comando.Parameters.AddWithValue("@NumeroAseguradora", !string.IsNullOrWhiteSpace(entidad.NumeroAseguradora) ? entidad.NumeroAseguradora : (object)DBNull.Value);
            comando.Parameters.AddWithValue("@TipoCertificado", !string.IsNullOrWhiteSpace(entidad.TipoCertificado) ? entidad.TipoCertificado : (object)DBNull.Value);

            conexion.Open();

            await comando.ExecuteNonQueryAsync();

        }

        public async Task<string> ObtenerPlacaParaScraping()
        {
            var resultado = default(string);


            using (var conexion = new SqlConnection(_configuracion.CadenaConexion))
            {
                using var comando = new SqlCommand("up_obtener_placa_para_scraping", conexion);
                comando.CommandType = CommandType.StoredProcedure;
                conexion.Open();

                using var reader = await comando.ExecuteReaderAsync(CommandBehavior.CloseConnection);
                while (reader.Read())
                {
                    resultado = !reader.IsDBNull(reader.GetOrdinal("Placa")) ? reader.GetString(reader.GetOrdinal("Placa")) : null;

                }


            }

            return resultado;
        }
    }
}
