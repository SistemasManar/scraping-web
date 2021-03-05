using System;
using System.Collections.Generic;
using System.Text;

namespace Consultas.Datos.Entidades
{
    public class SuneduTitulo
    {
        public string Dni { get; set; }

        public string Datos { get; set; }

        public DateTime Creado { get; set; }

        public DateTime Actualizado { get; set; }

        public SuneduTitulo()
        {
            Creado = DateTime.UtcNow;
            Actualizado = DateTime.UtcNow;
        }
    }
}
