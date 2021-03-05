using Consultas.Servicios.Infraestructura.Dtos;
using Consultas.WebApi.Infraestructura.Errores;
using Microsoft.AspNetCore.Mvc;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Threading.Tasks;

namespace Consultas.WebApi.Infraestructura.Controladores
{
    public class ControladorBase: ControllerBase
    {
        protected void GenerarBadRequestError(int codigoError, List<string> errores)
        {
            throw new ApiError(HttpStatusCode.BadRequest, codigoError, errores);
        }

        protected void GenerarNotFoundError(List<string> errores)
        {
            throw new ApiError(HttpStatusCode.NotFound, (int)HttpStatusCode.NotFound, errores);
        }

        protected void VerificarIfEsBuenJson<T>(T objeto)
            where T : class
        {
            if (objeto == default(T))
            {
                GenerarBadRequestError(400, new List<string>() { "Verifica que el json sigue el modelo establecido" });
            }
        }

        protected T ObtenerResultadoOGenerarErrorDeOperacion<T>(OperacionDto<T> operacion)
        {
            if (!operacion.Completado)
            {
                switch (operacion.Codigo)
                {
                    case CodigosOperacionDto.NoExiste:
                        GenerarNotFoundError(operacion.Mensajes);
                        break;
                    default:
                        GenerarBadRequestError((int)operacion.Codigo, operacion.Mensajes);
                        break;
                }
            }


            return operacion.Resultado;
        }
    }
}
