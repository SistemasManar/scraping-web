using Consultas.Datos.Entidades;
using System;
using System.Collections.Generic;
using System.Text;
using System.Threading.Tasks;

namespace Consultas.Datos.Daos.Abstracciones
{
    public interface IEmpresaDao
    {

        Task GuardarEmpresa(Empresa entidad);

        Task GuardarListaCantidadTrabajadores(List<CantidadTrabajador> trabajadores, string ruc);

        Task GuardarListaRepresentantes(List<Representante> representantes, string ruc);


        Task InsertarPadron(string nombre, string ruc);

        Task InsertarComprobantesElectronicos(string nombre, string ruc);

        Task InsertarSistemasDeEmisionElectronica(string nombre, string ruc);

        Task InsertarComprobantesDePago(string nombre, string ruc);

        Task InsertarActividadesEconomicas(string nombre, string codigo, string ruc);

        Task EliminarEmpresa(string ruc);

        Task<string> ObtenerRucParaScraping();
    }
}
