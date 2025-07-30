import logging
from typing import Any, Literal

import dns.rdata
import octodns.provider.base
import octodns.provider.plan
import octodns.record
import octodns.zone
import pynetbox.core.api
import pynetbox.core.response


class NetBoxDNSProvider(octodns.provider.base.BaseProvider):
    """OctoDNS provider for NetboxDNS"""

    SUPPORTS_GEO = False
    SUPPORTS_DYNAMIC = True  # pyright: ignore
    SUPPORTS_ROOT_NS = True
    SUPPORTS_MULTIVALUE_PTR = True

    # record types which are commented out, are not supported by the Netbox DNS plugin
    SUPPORTS = {  # noqa
        "A",
        "AAAA",
        # "ALIAS",
        "CAA",
        "CNAME",
        "DNAME",
        # "DS",
        "LOC",
        "MX",
        # "NAPTR",
        "NS",
        "PTR",
        # "SPF",
        "SRV",
        "SSHFP",
        # "TLSA",
        "TXT",
        # "URLFWD",
    }

    def __init__(
        self,
        id: int,  # noqa
        url: str,
        token: str,
        view: str | None | Literal[False] = None,
        replace_duplicates=False,
        make_absolute=False,
        disable_ptr=True,
        insecure_request=False,
        zone_status_filter="active",
        record_status_filter="active",
        max_page_size=0,
        *args,
        **kwargs,
    ) -> None:
        """initialize the NetBoxDNSProvider"""
        self.log = logging.getLogger(f"NetBoxDNSProvider[{id}]")

        super().__init__(id, *args, **kwargs)

        self.api = pynetbox.core.api.Api(url, token)
        if insecure_request:
            import urllib3  # noqa

            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            self.api.http_session.verify = False
        self.nb_view = self._get_nb_view(view)
        self.replace_duplicates = replace_duplicates
        self.make_absolute = make_absolute
        self.disable_ptr = disable_ptr
        self.zone_status_filter = {"status": zone_status_filter} if zone_status_filter else {}
        self.record_status_filter = {"status": record_status_filter} if record_status_filter else {}
        self.max_page_size = max_page_size

        _init_info = {k: v for k, v in locals().items() if k not in ["self", "__class__", "token"]}
        self.log.debug(f"__init__: {_init_info}")

    def _make_absolute(self, value: str, force: bool = False) -> str:
        """return dns name with trailing dot to make it absolute

        @param value: dns record value
        @param force: when `True`, disregard configuration option `make_absolute`

        @return: absolute dns record value
        """
        if value.endswith("."):
            return value

        if not (self.make_absolute or force):
            return value

        absolute_value = value + "."
        self.log.debug(f"relative={value}, absolute={absolute_value}")

        return absolute_value

    def _escape_semicolon(self, value: str) -> str:
        fixed = value.replace(";", r"\;")
        self.log.debug(rf"in='{value}', escaped='{fixed}'")
        return fixed

    def _unescape_semicolon(self, value: str) -> str:
        fixed = value.replace(r"\\", "\\").replace(r"\;", ";")
        self.log.debug(rf"in='{value}', unescaped='{fixed}'")
        return fixed

    def _get_nb_view(self, view: str | None | Literal[False]) -> dict[str, int]:
        """get the correct netbox view.
        views are required since netbox-plugin-dns>=1.0.0

        @param view: `None` for no view filter, else the view name

        @return: the netbox view id in the netbox query format
        """
        if not view:
            return {}

        nb_view: pynetbox.core.response.Record | None = self.api.plugins.netbox_dns.views.get(
            name=view
        )
        if nb_view is None:
            msg = f"dns view={view}, has not been found"
            self.log.error(msg)
            raise ValueError(msg)

        self.log.debug(f"found view={nb_view.name}, id={nb_view.id}")

        return {"view_id": nb_view.id}

    def _get_nb_zone(
        self,
        zone_name: str,
    ) -> pynetbox.core.response.Record:
        """given a zone name and a view name, look it up in NetBox.

        @param name: name of the dns zone
        @param view: the netbox view id in the api query format

        @raise pynetbox.RequestError: if declared view is not existent

        @return: the netbox dns zone object
        """
        nb_zone: pynetbox.core.response.Record | None = self.api.plugins.netbox_dns.zones.get(
            name=zone_name[:-1], **self.nb_view
        )

        if nb_zone is None:
            self.log.error(f"zone={zone_name}, not found in view={self.nb_view}")
            raise LookupError

        self.log.debug(f"found zone={nb_zone.name}, id={nb_zone.id}")

        return nb_zone

    def _format_rdata(self, rcd_type: str, rcd_value: str) -> str | dict[str, Any]:
        """format netbox record values to correct octodns record values

        @param rcd_type: record type
        @param rcd_value: record value

        @return: formatted rrdata value
        """
        rdata = dns.rdata.from_text("IN", rcd_type, rcd_value)
        match rdata.rdtype.name:
            case "A" | "AAAA":
                value = rdata.address

            case "CNAME" | "DNAME" | "NS" | "PTR":
                value = self._make_absolute(rdata.target.to_text())

            case "CAA":
                value = {
                    "flags": rdata.flags,
                    "tag": rdata.tag.decode(),
                    "value": rdata.value.decode(),
                }

            case "LOC":
                value = {
                    "lat_degrees": rdata.latitude[0],
                    "lat_minutes": rdata.latitude[1],
                    "lat_seconds": rdata.latitude[2] + rdata.latitude[3] / 1000,
                    "lat_direction": "N" if rdata.latitude[4] >= 0 else "S",
                    "long_degrees": rdata.longitude[0],
                    "long_minutes": rdata.longitude[1],
                    "long_seconds": rdata.longitude[2] + rdata.longitude[3] / 1000,
                    "long_direction": "W" if rdata.latitude[4] >= 0 else "E",
                    "altitude": rdata.altitude / 100,
                    "size": rdata.size / 100,
                    "precision_horz": rdata.horizontal_precision / 100,
                    "precision_vert": rdata.vertical_precision / 100,
                }

            case "MX":
                value = {
                    "preference": rdata.preference,
                    "exchange": self._make_absolute(rdata.exchange.to_text()),
                }

            case "NAPTR":
                value = {
                    "order": rdata.order,
                    "preference": rdata.preference,
                    "flags": rdata.flags,
                    "service": rdata.service,
                    "regexp": rdata.regexp,
                    "replacement": rdata.replacement.to_text(),
                }

            case "SSHFP":
                value = {
                    "algorithm": rdata.algorithm,
                    "fingerprint_type": rdata.fp_type,
                    "fingerprint": rdata.fingerprint.hex(),
                }

            case "TXT":
                value = self._escape_semicolon(rcd_value)

            case "SRV":
                value = {
                    "priority": rdata.priority,
                    "weight": rdata.weight,
                    "port": rdata.port,
                    "target": self._make_absolute(rdata.target.to_text()),
                }

            case "ALIAS" | "DS" | "NAPTR" | "SPF" | "TLSA" | "URLFWD" | "SOA":
                self.log.debug(f"'{rcd_type}' record type not implemented. ignoring record")
                raise NotImplementedError

            case _:
                self.log.error(f"ignoring invalid record with type: '{rcd_type}'")
                raise NotImplementedError

        self.log.debug(rf"formatted record value={value}")

        return value  # type:ignore

    def _format_nb_records(self, zone: octodns.zone.Zone) -> list[dict[str, Any]]:
        """format netbox dns records to the octodns format

        @param zone: octodns zone

        @return: a list of octodns compatible record dicts
        """
        records: dict[tuple[str, str], dict[str, Any]] = {}

        nb_zone = self._get_nb_zone(zone.name)
        nb_records: pynetbox.core.response.RecordSet = self.api.plugins.netbox_dns.records.filter(
            limit=self.max_page_size,
            zone_id=nb_zone.id,
            **self.record_status_filter,
        )
        for nb_record in nb_records:
            rcd_name: str = "" if nb_record.name == "@" else nb_record.name
            rcd_value: str = (
                self._make_absolute(nb_record.zone.name, True)
                if nb_record.value == "@"
                else nb_record.value
            )
            rcd_type: str = nb_record.type
            rcd_ttl: int = nb_record.ttl or nb_zone.default_ttl
            if nb_record.type == "NS":
                rcd_ttl = nb_zone.soa_refresh

            rcd_data = {
                "name": rcd_name,
                "type": rcd_type,
                "ttl": rcd_ttl,
                "values": [],
            }
            self.log.debug(rf"working on record={rcd_data}, value={rcd_value}")

            try:
                rcd_rdata = self._format_rdata(rcd_type, rcd_value)
            except NotImplementedError:
                continue

            if (rcd_name, rcd_type) not in records:
                records[(rcd_name, rcd_type)] = rcd_data

            records[(rcd_name, rcd_type)]["values"].append(rcd_rdata)

            self.log.debug(rf"record data={records[(rcd_name, rcd_type)]}")

        return list(records.values())

    def populate(
        self, zone: octodns.zone.Zone, target: bool = False, lenient: bool = False
    ) -> bool:
        """get all the records of a zone from NetBox and add them to the OctoDNS zone

        @param zone: octodns zone
        @param target: when `True`, load the current state of the provider.
        @param lenient: when `True`, skip record validation and do a "best effort" load of data.

        @return: true if the zone exists, else false.
        """
        self.log.info(f"--> populate '{zone.name}', target={target}, lenient={lenient}")

        try:
            records = self._format_nb_records(zone)
        except LookupError:
            return False

        for data in records:
            if len(data["values"]) == 1:
                data["value"] = data.pop("values")[0]
            record = octodns.record.Record.new(
                zone=zone,
                name=data["name"],
                data=data,
                source=self,
                lenient=lenient,
            )
            zone.add_record(record, lenient=lenient, replace=self.replace_duplicates)

        self.log.info(f"populate -> found {len(zone.records)} records for zone '{zone.name}'")

        return True

    def _format_changeset(self, change: Any) -> set[str]:
        """format the changeset

        @param change: the raw changes

        @return: the formatted/escaped changeset
        """
        match change._type:
            case "CAA":
                changeset = {repr(v) for v in change.values}
            case "TXT":
                changeset = {self._unescape_semicolon(repr(v)[1:-1]) for v in change.values}
            case _:
                match change:
                    case octodns.record.ValueMixin():
                        changeset = {repr(change.value)[1:-1]}
                    case octodns.record.ValuesMixin():
                        changeset = {repr(v)[1:-1] for v in change.values}
                    case _:
                        raise ValueError

        self.log.debug(f"{changeset=}")

        return changeset

    # def _include_change(self, change: octodns.record.change.Change) -> bool:
    #     """filter out record types which the provider can't create in netbox

    #     @param change: the planned change

    #     @return: false if the change should be discarded, true if it should be kept.
    #     """
    #     return True  # currently unused

    def _apply(self, plan: octodns.provider.plan.Plan) -> None:
        """apply the changes to the NetBox DNS zone.

        @param plan: the planned changes

        @return: none
        """
        self.log.debug(f"--> _apply zone={plan.desired.name}, changes={len(plan.changes)}")

        nb_zone = self._get_nb_zone(plan.desired.name)

        for change in plan.changes:
            match change:
                case octodns.record.Create():
                    rcd_name = "@" if change.new.name == "" else change.new.name

                    new_changeset = self._format_changeset(change.new)
                    for record in new_changeset:
                        self.log.debug(rf"ADD {change.new._type} {rcd_name} {record}")
                        self.api.plugins.netbox_dns.records.create(
                            zone=nb_zone.id,
                            name=rcd_name,
                            type=change.new._type,
                            ttl=change.new.ttl,
                            value=record,
                            disable_ptr=self.disable_ptr,
                        )

                case octodns.record.Delete():
                    nb_records: pynetbox.core.response.RecordSet = (
                        self.api.plugins.netbox_dns.records.filter(
                            limit=self.max_page_size,
                            zone_id=nb_zone.id,
                            name=change.existing.name,
                            type=change.existing._type,
                        )
                    )

                    existing_changeset = self._format_changeset(change.existing)
                    for nb_record in nb_records:
                        for record in existing_changeset:
                            if nb_record.value != record:
                                continue
                            self.log.debug(
                                rf"DELETE {nb_record.type} {nb_record.name} {nb_record.value}"
                            )
                            nb_record.delete()

                case octodns.record.Update():
                    rcd_name = "@" if change.existing.name == "" else change.existing.name

                    nb_records = self.api.plugins.netbox_dns.records.filter(
                        limit=self.max_page_size,
                        zone_id=nb_zone.id,
                        name=rcd_name,
                        type=change.existing._type,
                    )

                    existing_changeset = self._format_changeset(change.existing)
                    new_changeset = self._format_changeset(change.new)

                    to_delete = existing_changeset.difference(new_changeset)
                    to_update = existing_changeset.intersection(new_changeset)
                    to_create = new_changeset.difference(existing_changeset)

                    for nb_record in nb_records:
                        if nb_record.value in to_delete:
                            self.log.debug(
                                rf"DELETE {nb_record.type} {nb_record.name} {nb_record.value}"
                            )
                            nb_record.delete()
                        if nb_record.value in to_update:
                            self.log.debug(
                                rf"MODIFY (ttl) {nb_record.type} {nb_record.name} {nb_record.value}"
                            )
                            nb_record.ttl = change.new.ttl
                            nb_record.save()

                    for record in to_create:
                        self.log.debug(rf"ADD {change.new._type} {rcd_name} {record}")
                        nb_record = self.api.plugins.netbox_dns.records.create(
                            zone=nb_zone.id,
                            name=rcd_name,
                            type=change.new._type,
                            ttl=change.new.ttl,
                            value=record,
                            disable_ptr=self.disable_ptr,
                        )

    def list_zones(self) -> list[str]:
        """get all zones from netbox

        @return: a list with all active zones
        """
        zones = self.api.plugins.netbox_dns.zones.filter(
            limit=self.max_page_size, **self.nb_view, **self.zone_status_filter
        )
        absolute_zones = [self._make_absolute(z.name, True) for z in zones]

        return sorted(absolute_zones)
