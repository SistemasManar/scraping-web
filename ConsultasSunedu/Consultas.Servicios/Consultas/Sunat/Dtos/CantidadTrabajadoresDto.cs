using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Text;

namespace Consultas.Servicios.Consultas.Sunat.Dtos
{
    public class CantidadTrabajadoresDto
    {
        [JsonProperty(PropertyName = "periodo")]
        public string Periodo { get; set; }

        [JsonProperty(PropertyName = "nroTrabajadores")]
        public string NroTrabajadores { get; set; }

        [JsonProperty(PropertyName = "nroPensionistas")]
        public string NroPensionistas { get; set; }

        [JsonProperty(PropertyName = "nroPrestadoresDeServicio")]
        public string NroPrestadoresDeServicio { get; set; }
    }
}
