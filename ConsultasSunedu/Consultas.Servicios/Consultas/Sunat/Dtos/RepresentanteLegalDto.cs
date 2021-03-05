using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Text;

namespace Consultas.Servicios.Consultas.Sunat.Dtos
{
    public class RepresentanteLegalDto
    {
        [JsonProperty(PropertyName = "tipoDocumento")]
        public string TipoDocumento { get; set; }

        [JsonProperty(PropertyName = "nroDocumento")]
        public string NroDocumento { get; set; }

        [JsonProperty(PropertyName = "nombres")]
        public string Nombres { get; set; }

        [JsonProperty(PropertyName = "cargo")]
        public string Cargo { get; set; }

        [JsonProperty(PropertyName = "desde")]
        public string Desde { get; set; }
    }
}
