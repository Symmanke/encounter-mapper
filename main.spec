# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['main.py'],
             pathex=['/Users/ericsymmank/Documents/python/EncounterMapper'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
 a.datas += [('./Palette.json', './Palette.json', 'DATA'),
      ('./Group.json', './Group.json', 'DATA'),
      ('./Tile.json', './Tile.json', 'DATA'),
      ('./res/Title.png', './res/Title.png', 'DATA'),
      ('./res/bg_grass.png', './res/bg_grass.png', 'DATA'),
      ('./res/bg_tile.png', './res/bg_tile.png', 'DATA'),
      ('./res/bg_wood.png', './res/bg_wood.png', 'DATA')]


pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='main',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='main')
app = BUNDLE(coll,
             name='main.app',
             icon=None,
             bundle_identifier=None)
