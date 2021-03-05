using System;
using System.Collections.Generic;
using System.Text;
using Newtonsoft.Json;

namespace Consultas.Servicios.Consultas.Soat.Dtos
{
    public class RegistroSoatDto
    {
        [JsonProperty(PropertyName = "placa")]
        public string Placa { get; set; }

        [JsonProperty(PropertyName = "nombreCompania")]
        public string Compania { get; set; }

        [JsonProperty(PropertyName = "fechaInicio")]
        public string FechaInicio { get; set; }

        [JsonProperty(PropertyName = "fechaFin")]
        public string FechaFin { get; set; }

        [JsonProperty(PropertyName = "numeroPoliza")]
        public string NumeroPoliza { get; set; }

        [JsonProperty(PropertyName = "nombreUsoVehiculo")]
        public string UsoVehiculo { get; set; }

        [JsonProperty(PropertyName = "nombreClaseVehiculo")]
        public string ClaseVehiculo { get; set; }

        [JsonProperty(PropertyName = "estado")]
        public string Estado { get; set; }

        [JsonProperty(PropertyName = "codigoUnicoPoliza")]
        public string CodigoUnicoPoliza { get; set; }

        [JsonProperty(PropertyName = "codigoSBSAseguradora")]
        public string CodigoSbsAseguradora { get; set; }

        [JsonProperty(PropertyName = "fechaControlPolicial")]
        public string FechaControlPolicial { get; set; }

        [JsonProperty(PropertyName = "nombreContratante")]
        public string Contratante { get; set; }

        [JsonProperty(PropertyName = "nombreUbigeo")]
        public string Ubigeo { get; set; }

        [JsonProperty(PropertyName = "numeroSerieMotor")]
        public string SerieMotor { get; set; }

        [JsonProperty(PropertyName = "numeroSerieChasis")]
        public string SerieChasis { get; set; }

        [JsonProperty(PropertyName = "numeroAseguradora")]
        public string NumeroAseguradora { get; set; }

        [JsonProperty(PropertyName = "tipoCertificado")]
        public string TipoCertificado { get; set; }

        [JsonProperty(PropertyName = "fechaCreacion")]
        public string FechaCreacion { get; set; }
    }
}
