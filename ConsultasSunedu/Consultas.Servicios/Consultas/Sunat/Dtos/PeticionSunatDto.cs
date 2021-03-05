using System;
using System.Collections.Generic;
using System.Text;

namespace Consultas.Servicios.Consultas.Sunat.Dtos
{
    public class PeticionSunatDto
    {
        public string Ruc { get; set; }

        public string RazonSocial { get; set; }

        public string CodigoCaptcha { get; set; }
    }
}
