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
    public class EmpresaDao : IEmpresaDao
    {

        private readonly DatabaseConfiguracion _configuracion;

        public EmpresaDao(
            DatabaseConfiguracion configuracion
            )
        {
            _configuracion = configuracion;
        }


        public async Task EliminarEmpresa(string ruc)
        {
            using var conexion = new SqlConnection(_configuracion.CadenaConexion);
            using var comando = new SqlCommand("up_eliminar_empresa", conexion);
            comando.CommandType = CommandType.StoredProcedure;
            comando.Parameters.AddWithValue("@ruc", ruc);
            conexion.Open();
            await comando.ExecuteNonQueryAsync();
        }

        public async Task GuardarEmpresa(Empresa entidad)
        {
            using var conexion = new SqlConnection(_configuracion.CadenaConexion);
            using var comando = new SqlCommand("up_insertar_empresa", conexion);
            comando.CommandType = CommandType.StoredProcedure;
            comando.Parameters.AddWithValue("@ruc", entidad.Ruc);
            comando.Parameters.AddWithValue("@tipoContribuyente", !string.IsNullOrWhiteSpace(entidad.TipoContribuyente) ? entidad.TipoContribuyente : (object)DBNull.Value);
            comando.Parameters.AddWithValue("@nombre", !string.IsNullOrWhiteSpace(entidad.Nombre) ? entidad.Nombre : (object)DBNull.Value);
            comando.Parameters.AddWithValue("@nombreComercial", !string.IsNullOrWhiteSpace(entidad.NombreComercial) ? entidad.NombreComercial : (object)DBNull.Value);
            comando.Parameters.AddWithValue("@fechaInscripcion", !string.IsNullOrWhiteSpace(entidad.FechaInscripcion) ? entidad.FechaInscripcion : (object)DBNull.Value);
            comando.Parameters.AddWithValue("@fechaInicioActividades", !string.IsNullOrWhiteSpace(entidad.FechaInicioActividades) ? entidad.FechaInicioActividades : (object)DBNull.Value);
            comando.Parameters.AddWithValue("@estadoContribuyente", !string.IsNullOrWhiteSpace(entidad.EstadoContribuyente) ? entidad.EstadoContribuyente : (object)DBNull.Value);
            comando.Parameters.AddWithValue("@condicionContribuyente", !string.IsNullOrWhiteSpace(entidad.CondicionContribuyente) ? entidad.CondicionContribuyente : (object)DBNull.Value);
            comando.Parameters.AddWithValue("@direccionDomicilioFiscal", !string.IsNullOrWhiteSpace(entidad.DireccionDomicilioFiscal) ? entidad.DireccionDomicilioFiscal : (object)DBNull.Value);
            comando.Parameters.AddWithValue("@departamentoDomicilioFiscal", !string.IsNullOrWhiteSpace(entidad.DepartamentoDomicilioFiscal) ? entidad.DepartamentoDomicilioFiscal : (object)DBNull.Value);
            comando.Parameters.AddWithValue("@provinciaDomicilioFiscal", !string.IsNullOrWhiteSpace(entidad.ProvinciaDomicilioFiscal) ? entidad.ProvinciaDomicilioFiscal : (object)DBNull.Value);
            comando.Parameters.AddWithValue("@distritoDomicilioFiscal", !string.IsNullOrWhiteSpace(entidad.DistritoDomicilioFiscal) ? entidad.DistritoDomicilioFiscal : (object)DBNull.Value);
            comando.Parameters.AddWithValue("@sistemaEmisionComprobante", !string.IsNullOrWhiteSpace(entidad.SistemaEmisionComprobante) ? entidad.SistemaEmisionComprobante : (object)DBNull.Value);
            comando.Parameters.AddWithValue("@actividadComercioExterior", !string.IsNullOrWhiteSpace(entidad.ActividadComercioExterior) ? entidad.ActividadComercioExterior : (object)DBNull.Value);
            comando.Parameters.AddWithValue("@sistemaDeContabilidad", !string.IsNullOrWhiteSpace(entidad.SistemaDeContabilidad) ? entidad.SistemaDeContabilidad : (object)DBNull.Value);
            comando.Parameters.AddWithValue("@emisorElectronicoDesde", !string.IsNullOrWhiteSpace(entidad.EmisorElectronicoDesde) ? entidad.EmisorElectronicoDesde : (object)DBNull.Value);
            comando.Parameters.AddWithValue("@afiliadoPLEDesde", !string.IsNullOrWhiteSpace(entidad.AfiliadoPLEDesde) ? entidad.AfiliadoPLEDesde : (object)DBNull.Value);

            conexion.Open();

            await comando.ExecuteNonQueryAsync();
        }

        public async Task GuardarListaCantidadTrabajadores(List<CantidadTrabajador> trabajadores, string ruc)
        {
            if (trabajadores == null)
            {
                return;
            }

            foreach (var trabajador in trabajadores)
            {
                await GuardarTrabajador(trabajador, ruc);
            }
        }

        public async Task GuardarListaRepresentantes(List<Representante> representantes, string ruc)
        {
            if (representantes == null)
            {
                return;
            }

            foreach (var representante in representantes)
            {
                await GuardarRepresentante(representante, ruc);
            }
        }

        public async Task InsertarActividadesEconomicas(string nombre, string codigo, string ruc)
        {
            using var conexion = new SqlConnection(_configuracion.CadenaConexion);
            using var comando = new SqlCommand("up_insertar_ActividadesEconomicas", conexion);
            comando.CommandType = CommandType.StoredProcedure;
            comando.Parameters.AddWithValue("@ruc", ruc);
            comando.Parameters.AddWithValue("@codigo", codigo);
            comando.Parameters.AddWithValue("@actividadesEconomica", !string.IsNullOrWhiteSpace(nombre) ? nombre : (object)DBNull.Value);

            conexion.Open();

            await comando.ExecuteNonQueryAsync();
        }

        public async Task InsertarComprobantesDePago(string nombre, string ruc)
        {
            using var conexion = new SqlConnection(_configuracion.CadenaConexion);
            using var comando = new SqlCommand("up_insertar_ComprobantesDePago", conexion);
            comando.CommandType = CommandType.StoredProcedure;
            comando.Parameters.AddWithValue("@ruc", ruc);
            comando.Parameters.AddWithValue("@comprobanteDePago", !string.IsNullOrWhiteSpace(nombre) ? nombre : (object)DBNull.Value);

            conexion.Open();

            await comando.ExecuteNonQueryAsync();
        }

        public async Task InsertarComprobantesElectronicos(string nombre, string ruc)
        {
            using var conexion = new SqlConnection(_configuracion.CadenaConexion);
            using var comando = new SqlCommand("up_insertar_ComprobantesElectronicos", conexion);
            comando.CommandType = CommandType.StoredProcedure;
            comando.Parameters.AddWithValue("@ruc", ruc);
            comando.Parameters.AddWithValue("@omprobanteElectronicos", !string.IsNullOrWhiteSpace(nombre) ? nombre : (object)DBNull.Value);

            conexion.Open();

            await comando.ExecuteNonQueryAsync();
        }

        public async Task InsertarPadron(string nombre, string ruc)
        {
            using var conexion = new SqlConnection(_configuracion.CadenaConexion);
            using var comando = new SqlCommand("up_insertar_Padrones", conexion);
            comando.CommandType = CommandType.StoredProcedure;
            comando.Parameters.AddWithValue("@ruc", ruc);
            comando.Parameters.AddWithValue("@padron", !string.IsNullOrWhiteSpace(nombre) ? nombre : (object)DBNull.Value);

            conexion.Open();

            await comando.ExecuteNonQueryAsync();
        }

        public async Task InsertarSistemasDeEmisionElectronica(string nombre, string ruc)
        {
            using var conexion = new SqlConnection(_configuracion.CadenaConexion);
            using var comando = new SqlCommand("up_insertar_SistemasDeEmisionElectronica", conexion);
            comando.CommandType = CommandType.StoredProcedure;
            comando.Parameters.AddWithValue("@ruc", ruc);
            comando.Parameters.AddWithValue("@sistemaDeEmisionElectronica", !string.IsNullOrWhiteSpace(nombre) ? nombre : (object)DBNull.Value);

            conexion.Open();

            await comando.ExecuteNonQueryAsync();
        }


        private async Task GuardarTrabajador(CantidadTrabajador dto, string ruc)
        {
            using var conexion = new SqlConnection(_configuracion.CadenaConexion);
            using var comando = new SqlCommand("up_insertar_cantidadTrabajadores", conexion);
            comando.CommandType = CommandType.StoredProcedure;
            comando.Parameters.AddWithValue("@ruc", ruc);
            comando.Parameters.AddWithValue("@periodo", !string.IsNullOrWhiteSpace(dto.Periodo) ? dto.Periodo : (object)DBNull.Value);
            comando.Parameters.AddWithValue("@nroTrabajadores", !string.IsNullOrWhiteSpace(dto.NroTrabajadores) ? dto.NroTrabajadores : (object)DBNull.Value);
            comando.Parameters.AddWithValue("@nroPensionistas", !string.IsNullOrWhiteSpace(dto.NroPensionistas) ? dto.NroPensionistas : (object)DBNull.Value);
            comando.Parameters.AddWithValue("@nroPrestadoresServicio", !string.IsNullOrWhiteSpace(dto.NroPrestadoresDeServicio) ? dto.NroPrestadoresDeServicio : (object)DBNull.Value);

            conexion.Open();

            await comando.ExecuteNonQueryAsync();
        }

        private async Task GuardarRepresentante(Representante dto, string ruc)
        {

            using var conexion = new SqlConnection(_configuracion.CadenaConexion);
            using var comando = new SqlCommand("up_insertar_representante", conexion);
            comando.CommandType = CommandType.StoredProcedure;
            comando.Parameters.AddWithValue("@ruc", ruc);
            comando.Parameters.AddWithValue("@tipoDocumento", !string.IsNullOrWhiteSpace(dto.TipoDocumento) ? dto.TipoDocumento : (object)DBNull.Value);
            comando.Parameters.AddWithValue("@nroDocumento", !string.IsNullOrWhiteSpace(dto.NroDocumento) ? dto.NroDocumento : (object)DBNull.Value);
            comando.Parameters.AddWithValue("@nombres", !string.IsNullOrWhiteSpace(dto.Nombres) ? dto.Nombres : (object)DBNull.Value);
            comando.Parameters.AddWithValue("@cargo", !string.IsNullOrWhiteSpace(dto.Cargo) ? dto.Cargo : (object)DBNull.Value);
            comando.Parameters.AddWithValue("@desde", !string.IsNullOrWhiteSpace(dto.Desde) ? dto.Desde : (object)DBNull.Value);

            conexion.Open();

            await comando.ExecuteNonQueryAsync();

        }

        public async Task<string> ObtenerRucParaScraping()
        {
            var resultado = default(string);


            using (var conexion = new SqlConnection(_configuracion.CadenaConexion))
            {
                using var comando = new SqlCommand("up_obtener_ruc_para_scraping", conexion);
                comando.CommandType = CommandType.StoredProcedure;
                conexion.Open();

                using var reader = await comando.ExecuteReaderAsync(CommandBehavior.CloseConnection);
                while (reader.Read())
                {
                    resultado = !reader.IsDBNull(reader.GetOrdinal("Ruc")) ? reader.GetString(reader.GetOrdinal("Ruc")) : null;

                }


            }

            return resultado;
        }
    }
}
