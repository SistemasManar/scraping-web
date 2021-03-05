using Consultas.Datos.Daos.Abstracciones;
using Consultas.Datos.Entidades;
using Consultas.Servicios.Consultas.Sunat.Dtos;
using Consultas.Servicios.Consultas.Sunat.Servicios.Abstracciones;
using Consultas.Servicios.Consultas.Sunat.Trabajadores.Abstracciones;
using Hangfire;
using System;
using System.Collections.Generic;
using System.Text;
using System.Threading.Tasks;

namespace Consultas.Servicios.Consultas.Sunat.Trabajadores.Implementaciones
{
    public class SunatTrabajador : ISunatTrabajador
    {

        private IEmpresaDao _empresaDao;
        private ISunatServicio _sunatServicio;


        public SunatTrabajador(
            IEmpresaDao empresaDao,
            ISunatServicio sunatServicio
            )
        {
            _empresaDao = empresaDao;
            _sunatServicio = sunatServicio;
        }

        public async Task RealizarTrabajo(IJobCancellationToken cancellationToken)
        {
            while (true)
            {
                var hora = DateTime.Now.Hour;
                var delay = 20000;

                if (hora >= 6 && hora < 23)
                {
                    delay = 10000;
                }

                try
                {
                    await RealizarScraping();
                }
                catch { }

                cancellationToken.ThrowIfCancellationRequested();
                await Task.Delay(delay);
            }
        }


        private async Task RealizarScraping()
        {
            var ruc = await _empresaDao.ObtenerRucParaScraping();
            if (string.IsNullOrWhiteSpace(ruc))
            {
                return;
            }

            var peticion = new PeticionSunatDto()
            {
                Ruc = ruc
            };

            var operacion = await _sunatServicio.BuscarEmpresa(peticion);

            if (!operacion.Completado || string.IsNullOrWhiteSpace(operacion.Resultado.FechaInscripcion))
            {
                return;
            }


            var dto = operacion.Resultado;

            var empresa = new Empresa()
            {
                ActividadComercioExterior = dto.ActividadComercioExterior,
                AfiliadoPLEDesde = dto.AfiliadoPLEDesde,
                CondicionContribuyente = dto.CondicionContribuyente,
                DepartamentoDomicilioFiscal = dto.DepartamentoDomicilioFiscal,
                DireccionDomicilioFiscal = dto.DireccionDomicilioFiscal,
                DistritoDomicilioFiscal = dto.DistritoDomicilioFiscal,
                EmisorElectronicoDesde = dto.EmisorElectronicoDesde,
                EstadoContribuyente = dto.EstadoContribuyente,
                FechaInicioActividades = dto.FechaInicioActividades,
                FechaInscripcion = dto.FechaInscripcion,
                Nombre = dto.Nombre,
                NombreComercial = dto.NombreComercial,
                ProvinciaDomicilioFiscal = dto.ProvinciaDomicilioFiscal,
                Ruc = dto.Ruc,
                SistemaDeContabilidad = dto.SistemaDeContabilidad,
                SistemaEmisionComprobante = dto.SistemaEmisionComprobante,
                TipoContribuyente = dto.TipoContribuyente
            };

            await _empresaDao.EliminarEmpresa(dto.Ruc);
            await _empresaDao.GuardarEmpresa(empresa);


            if (dto.Padrones != null)
            {

                foreach (var padron in dto.Padrones)
                {
                    await _empresaDao.InsertarPadron(padron, dto.Ruc);
                }
            }

            if (dto.ComprobantesElectronicos != null)
            {

                foreach (var comprobante in dto.ComprobantesElectronicos)
                {
                    await _empresaDao.InsertarComprobantesElectronicos(comprobante, dto.Ruc);
                }
            }

            if (dto.SistemasDeEmisionElectronica != null)
            {

                foreach (var emision in dto.SistemasDeEmisionElectronica)
                {
                    await _empresaDao.InsertarSistemasDeEmisionElectronica(emision, dto.Ruc);
                }
            }

            if (dto.ComprobantesDePago != null)
            {

                foreach (var comprobante in dto.ComprobantesDePago)
                {
                    await _empresaDao.InsertarComprobantesDePago(comprobante, dto.Ruc);
                }
            }


            if (dto.ActividadesEconomicas != null)
            {

                foreach (var actividad in dto.ActividadesEconomicas)
                {
                    var partes = actividad.Split(new string[] { "-" }, StringSplitOptions.None);
                    var nombreActividad = "";
                    var codigoActividad = "";

                    if (partes.Length < 2)
                    {
                        continue;
                    }

                    codigoActividad = partes[0];
                    nombreActividad = partes[1];

                    if (!string.IsNullOrWhiteSpace(nombreActividad))
                    {
                        nombreActividad = nombreActividad.Trim();
                    }

                    if (!string.IsNullOrWhiteSpace(codigoActividad))
                    {
                        codigoActividad = codigoActividad.Trim();
                    }

                    await _empresaDao.InsertarActividadesEconomicas(nombreActividad, codigoActividad, dto.Ruc);
                }
            }

            if (dto.Representantes != null)
            {
                var lista = new List<Representante>();

                foreach (var representante in dto.Representantes)
                {
                    lista.Add(
                        new Representante()
                        {
                            Cargo = representante.Cargo,
                            Desde = representante.Desde,
                            Nombres = representante.Nombres,
                            NroDocumento = representante.NroDocumento,
                            TipoDocumento = representante.TipoDocumento
                        }
                        );
                }

                await _empresaDao.GuardarListaRepresentantes(lista, dto.Ruc);
            }


            if (dto.CantidadTrabajadores != null)
            {
                var lista = new List<CantidadTrabajador>();

                foreach (var trabajador in dto.CantidadTrabajadores)
                {
                    lista.Add(
                        new CantidadTrabajador()
                        {
                            NroPensionistas = trabajador.NroPensionistas,
                            NroPrestadoresDeServicio = trabajador.NroPrestadoresDeServicio,
                            NroTrabajadores = trabajador.NroTrabajadores,
                            Periodo = trabajador.Periodo
                        }
                        );
                }

                await _empresaDao.GuardarListaCantidadTrabajadores(lista, dto.Ruc);
            }

        }
    }
}
