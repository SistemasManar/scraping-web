using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Text;

namespace Consultas.Servicios.Consultas.Sunedu.Dtos
{
    public class TituloScraperDto
    {

        [JsonProperty(PropertyName = "ID")]
        public string Id { get; set; }

        [JsonProperty(PropertyName = "NOMBRE")]
        public string Nombre { get; set; }

        [JsonProperty(PropertyName = "DOC_IDENT")]
        public string DocIdent { get; set; }

        [JsonProperty(PropertyName = "GRADO")]
        public string Grado { get; set; }

        [JsonProperty(PropertyName = "TITULO_REV")]
        public string TituloRev { get; set; }

        [JsonProperty(PropertyName = "GRADO_REV")]
        public string GradoRev { get; set; }

        [JsonProperty(PropertyName = "DIPL_FEC")]
        public string DiplFec { get; set; }

        [JsonProperty(PropertyName = "RESO_FEC")]
        public string ResoFec { get; set; }

        [JsonProperty(PropertyName = "ESSUNEDU")]
        public string EsSunedu { get; set; }

        [JsonProperty(PropertyName = "UNIV")]
        public string Univ { get; set; }

        [JsonProperty(PropertyName = "PAIS")]
        public string Pais { get; set; }

        [JsonProperty(PropertyName = "COMENTARIO")]
        public string Comentario { get; set; }

        [JsonProperty(PropertyName = "TIPO")]
        public string Tipo { get; set; }

        [JsonProperty(PropertyName = "TIPO_GRADO")]
        public string TipoGrado { get; set; }

        [JsonProperty(PropertyName = "DIPL_TIP_EMI")]
        public string DiplTipEmi { get; set; }
        
        [JsonProperty(PropertyName = "TIPO_INSCRI")]
        public string TipoInscri { get; set; }

        [JsonProperty(PropertyName = "NUM_DIPL_REVA")]
        public string NumDiplReva { get; set; }

        [JsonProperty(PropertyName = "NUM_ORD_PAG")]
        public string NumOrdPag { get; set; }

        [JsonProperty(PropertyName = "V_ORIGEN")]
        public string VOrigen { get; set; }

        [JsonProperty(PropertyName = "NRO_RESOLUCION_NULIDAD")]
        public string NroResolucionNulidad { get; set; }

        [JsonProperty(PropertyName = "FLG_RESOLUCION_NULIDAD")]
        public string FlagResolucionNulidad { get; set; }

        [JsonProperty(PropertyName = "FECHA_RESOLUCION_NULIDAD")]
        public string FechaResolucionNulidad { get; set; }

    }
}
