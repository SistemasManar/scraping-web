using System;
using System.Collections.Generic;
using System.Text;

namespace Consultas.Servicios.Infraestructura.Dtos
{
    public enum CodigosOperacionDto
    {
        Suceso,
        ResultadoVacio,
        UsuarioIncorrecto,
        UsuarioInhabilitado,
        OperacionNoDisponible,
        AccesoInvalido,
        NoExiste,
        ErrorServidor,
        ServidorSmsError,
        Invalido,
        NoTienSBS,
        YaExisteSolicitud,
        CaptchaIncorrecto = 411,
        DniInexistente = 410,
        NoSePudoRealizarPago = 1034,
        CamposRequeridos = 400,
        OperacionYaRealizada = 440,
        LaDistanciaSuperaElLimite = 2500,
        NoSePudoEnviarCodigoDeAcceso = 1100,
        SinAccesoSunat
    };
}
