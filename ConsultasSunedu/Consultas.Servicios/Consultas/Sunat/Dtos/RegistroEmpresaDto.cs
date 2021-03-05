using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Text;

namespace Consultas.Servicios.Consultas.Sunat.Dtos
{
    public class RegistroEmpresaDto
    {
        [JsonProperty(PropertyName = "ruc")]
        public string Ruc { get; set; }

        [JsonProperty(PropertyName = "tipoContribuyente")]
        public string TipoContribuyente { get; set; }

        [JsonProperty(PropertyName = "nombre")]
        public string Nombre { get; set; }

        [JsonProperty(PropertyName = "nombreComercial")]
        public string NombreComercial { get; set; }

        [JsonProperty(PropertyName = "fechaInscripcion")]
        public string FechaInscripcion { get; set; }

        [JsonProperty(PropertyName = "fechaInicioActividades")]
        public string FechaInicioActividades { get; set; }

        [JsonProperty(PropertyName = "estadoContribuyente")]
        public string EstadoContribuyente { get; set; }

        [JsonProperty(PropertyName = "condicionContribuyente")]
        public string CondicionContribuyente { get; set; }

        [JsonProperty(PropertyName = "direccionDomicilioFiscal")]
        public string DireccionDomicilioFiscal { get; set; }

        [JsonProperty(PropertyName = "departamentoDomicilioFiscal")]
        public string DepartamentoDomicilioFiscal { get; set; }

        [JsonProperty(PropertyName = "provinciaDomicilioFiscal")]
        public string ProvinciaDomicilioFiscal { get; set; }

        [JsonProperty(PropertyName = "distritoDomicilioFiscal")]
        public string DistritoDomicilioFiscal { get; set; }

        [JsonProperty(PropertyName = "sistemaEmisionComprobante")]
        public string SistemaEmisionComprobante { get; set; }

        [JsonProperty(PropertyName = "actividadComercioExterior")]
        public string ActividadComercioExterior { get; set; }

        [JsonProperty(PropertyName = "sistemaDeContabilidad")]
        public string SistemaDeContabilidad { get; set; }

        [JsonProperty(PropertyName = "actividadesEconomicas")]
        public List<string> ActividadesEconomicas { get; set; }

        [JsonProperty(PropertyName = "comprobantesDePago")]
        public List<string> ComprobantesDePago { get; set; }

        [JsonProperty(PropertyName = "sistemasDeEmisionElectronica")]
        public List<string> SistemasDeEmisionElectronica { get; set; }

        [JsonProperty(PropertyName = "emisorElectronicoDesde")]
        public string EmisorElectronicoDesde { get; set; }

        [JsonProperty(PropertyName = "comprobantesElectronicos")]
        public List<string> ComprobantesElectronicos { get; set; }

        [JsonProperty(PropertyName = "afiliadoPLEDesde")]
        public string AfiliadoPLEDesde { get; set; }

        [JsonProperty(PropertyName = "padrones")]
        public List<string> Padrones { get; set; }

        [JsonProperty(PropertyName = "cantidadTrabajadores")]
        public List<CantidadTrabajadoresDto> CantidadTrabajadores { get; set; }

        [JsonProperty(PropertyName = "representantes")]
        public List<RepresentanteLegalDto> Representantes { get; set; }

        public RegistroEmpresaDto()
        {
            ActividadesEconomicas = new List<string>();
            ComprobantesDePago = new List<string>();
            SistemasDeEmisionElectronica = new List<string>();
            ComprobantesElectronicos = new List<string>();
            Padrones = new List<string>();
            CantidadTrabajadores = new List<CantidadTrabajadoresDto>();
            Representantes = new List<RepresentanteLegalDto>();
        }
    }
}
