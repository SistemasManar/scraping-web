using System;
using System.Collections.Generic;
using System.Text;

namespace Consultas.Datos.Entidades
{
    public class Empresa
    {

        public string Ruc { get; set; }

        public string TipoContribuyente { get; set; }

        public string Nombre { get; set; }

        public string NombreComercial { get; set; }

        public string FechaInscripcion { get; set; }

        public string FechaInicioActividades { get; set; }

        public string EstadoContribuyente { get; set; }

        public string CondicionContribuyente { get; set; }

        public string DireccionDomicilioFiscal { get; set; }

        public string DepartamentoDomicilioFiscal { get; set; }

        public string ProvinciaDomicilioFiscal { get; set; }

        public string DistritoDomicilioFiscal { get; set; }

        public string SistemaEmisionComprobante { get; set; }

        public string ActividadComercioExterior { get; set; }

        public string SistemaDeContabilidad { get; set; }

        public string EmisorElectronicoDesde { get; set; }

        public string AfiliadoPLEDesde { get; set; }
    }
}
