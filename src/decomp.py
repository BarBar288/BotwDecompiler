import asyncio
import exts
import subprocess
import oead
import os

from bcml import util
from botw_havok import Havok
from pathlib import Path
from utils import error


def aamp(file: Path, out: Path):
    """Decompile an aamp file"""

    try:
        data = file.read_bytes()

        if data[0:4] == b"Yaz0":
            data = oead.yaz0.decompress(data)

        if data[0:4] != b"AAMP":
            error(
                f"[WARNING] Could not decompile '{file}' because it was not a valid AAMP file!"
            )
            return

        cdir(out)

        data = oead.aamp.ParameterIO.from_binary(data)
        data = oead.aamp.ParameterIO.to_text(data)

        Path(f"{out}.yml").write_text(data)

    except RuntimeError as ex:
        error(f"[AAMP] {ex}")


def bars(file: Path, out: Path):
    """Decompile a bars file"""

    from imported.bars_extractor import extract

    try:
        cdir(out, True)
        extract(file, out)
    except RuntimeError as ex:
        error(f"[BARS] {ex}")


def evfl(file: Path, out: Path):
    """Decompile a bfevfl file"""

    from imported.evfl_to_json import convert

    try:
        cdir(out)
        out.write_text(convert(file))
    except RuntimeError as ex:
        error(f"[EVFL] {ex}")


def bfres(file: Path, out: Path):
    """Decompile a bfres file"""

    try:
        cdir(out, True)
        subprocess.check_call([".\\lib\\DecompileBfres.exe", f"{file}", f"{out}"])
    except RuntimeError as ex:
        error(f"[BFRES] {ex}")


def byml(file: Path, out: Path):
    """Decompile a byml file"""

    try:
        data = file.read_bytes()

        if data[0:4] == b"Yaz0":
            data = oead.yaz0.decompress(data)

        if data[0:2] != b"BY" and data[0:2] != b"YB":
            error(
                f"[WARNING] Could not decompile '{file}' because it was not a valid BYML file!"
            )
            return

        cdir(out)

        data = oead.byml.from_binary(data)
        data = oead.byml.to_text(data)

        Path(f"{out}.yml").write_text(data)

    except RuntimeError as ex:
        error(f"[BYML] {ex}")


def havok(file: Path, out: Path):
    """Decompile a havok file"""
    try:
        cdir(out)
        hk = Havok.from_file(file)
        hk.deserialize()
        hk.to_json(Path(f"{out}.json"))
    except RuntimeError as ex:
        error(f"[HAVOK] {ex}")


def msbt(file: Path, out: Path):
    """Decompile a msbt file"""

    try:
        cdir(out)
        subprocess.check_call(
            [".\\lib\\Msyt.exe", "export", f"-o", f"{out}.yml", f"{file}"]
        )
    except RuntimeError as ex:
        error(f"[MSBT] {ex}")


def sarc(file: Path, out: Path):
    """Decompile a sarc file"""

    try:

        data = file.read_bytes()

        if data == None or len(data) < 4:
            error(
                f"[WARNING] Could not decompile '{file}' because it was not a valid SARC file!"
            )
            return

        if data[0:4] == b"Yaz0":
            data = oead.yaz0.decompress(data)

        if data[0:4] != b"SARC":
            error(
                f"[WARNING] Could not decompile '{file}' because it was not a valid SARC file!"
            )
            return

        cdir(out)

        data = oead.Sarc(data)
        tasks = []

        for sfile in data.get_files():

            is_del: bool = True
            out_file = Path(out, sfile.name)

            cdir(out_file)

            ext = out_file.suffix
            out_file.write_bytes(sfile.data)

            if ext in exts.BARS_EXT:
                tasks.append(asyncio.create_task(bars(out_file, out_file)))
            elif ext in exts.BFEVFL_EXT:
                tasks.append(asyncio.create_task(evfl(out_file, out_file)))
            elif ext in exts.BFRES_EXT:
                tasks.append(asyncio.create_task(bfres(out_file, out_file)))
            elif ext in util.BYML_EXTS:
                tasks.append(asyncio.create_task(byml(out_file, out_file)))
            elif ext in exts.HK_EXT:
                tasks.append(asyncio.create_task(havok(out_file, out_file)))
            elif ext in exts.MSBT_EXT:
                tasks.append(asyncio.create_task(msbt(out_file, out_file)))
            elif ext in util.SARC_EXTS:
                tasks.append(asyncio.create_task(sarc(out_file, out_file)))
            else:
                is_del = False

            if is_del:
                out_file.unlink()

        asyncio.gather(*tasks)

    except RuntimeError as ex:
        error(f"[MSBT] {ex}")


def copy(file: Path, out: Path):

    try:

        data = file.read_bytes()
        cdir(out)
        Path(out).write_bytes(data)

        print(f"[COPY] {os.path.basename(file)}")

    except RuntimeError as ex:
        error(f"[MSBT] {ex}")


def cdir(out: Path, is_archive: bool = False):

    if is_archive:
        os.makedirs(out, exist_ok=True)
    else:
        os.makedirs(os.path.dirname(out), exist_ok=True)
