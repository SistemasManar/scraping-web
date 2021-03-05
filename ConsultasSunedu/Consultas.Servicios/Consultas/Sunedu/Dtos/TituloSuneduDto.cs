using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Text;

namespace Consultas.Servicios.Consultas.Sunedu.Dtos
{
    public class TituloSuneduDto
    {
        [JsonProperty(PropertyName ="nombreCompleto")]
        public string NombreCompleto { get; set; }

        [JsonProperty(PropertyName = "titulo")]
        public string Titulo { get; set; }

        [JsonProperty(PropertyName = "fechaDiploma")]
        public string FechaDiploma { get; set; }

        [JsonProperty(PropertyName = "institucion")]
        public string Institucion { get; set; }

    }
}
