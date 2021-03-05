using System;
using System.Collections.Generic;
using System.Text;

namespace Consultas.Servicios.Consultas.Sunedu.Dtos
{
    public class SuneduConfiguracionDto
    {
        public string RutaTesseract { get; set; }

        public string RutaFolderTrabajo { get; set; }

        public string UrlSunedu { get; set; }

        public string UserAgent { get; set; }
    }
}
