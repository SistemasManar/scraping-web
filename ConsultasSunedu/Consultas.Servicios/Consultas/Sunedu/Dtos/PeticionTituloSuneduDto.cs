using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Text;

namespace Consultas.Servicios.Consultas.Sunedu.Dtos
{
    public class PeticionTituloSuneduDto
    {
        [JsonProperty(PropertyName = "dni")]
        public string Dni { get; set; }

        [JsonIgnore]
        public string RutaTesseract { get; set; }

        [JsonIgnore]
        public string RutaFolderTrabajo { get; set; }

        [JsonIgnore]
        public string UrlSunedu { get; set; }

        [JsonIgnore]
        public string UserAgent { get; set; }
    }
}
