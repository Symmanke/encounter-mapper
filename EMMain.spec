# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['EMMain.py'],
             pathex=['/Users/ericsymmank/Documents/python/EncounterMapper'],
             binaries=[],
             datas=[],
             hiddenimports=['PyQt5', 'PyQt5.QtWidgets'],
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
  ('./Texture.json', './Texture.json', 'DATA'),
  ('./res/Title.png', './res/Title.png', 'DATA'),
  ('./res/bg_grass.png', './res/bg_grass.png', 'DATA'),
  ('./res/bg_tile.png', './res/bg_tile.png', 'DATA'),
  ('./res/bg_wood.png', './res/bg_wood.png', 'DATA'),
  ('./res/bg_lava_1.png', './res/bg_lava_1.png', 'DATA'),
  ('./res/bg_lava_2.png', './res/bg_lava_2.png', 'DATA'),
  ('./res/bg_water.png', './res/bg_water.png', 'DATA'),
  ('./res/bg_cobblestone.png', './res/bg_cobblestone.png', 'DATA'),
  ('./res/bg_checkerboard.png', './res/bg_checkerboard.png', 'DATA'),
  ('./res/bg_gradient.png', './res/bg_gradient.png', 'DATA'),
  ('./res/Icon.png', './res/Icon.png', 'DATA'),
  ('./res/Icon.icns', './res/Icon.icns', 'DATA'),
  ('./res/note_icons/0.png', './res/note_icons/0.png', 'DATA'),
  ('./res/note_icons/1.png', './res/note_icons/1.png', 'DATA'),
  ('./res/note_icons/2.png', './res/note_icons/2.png', 'DATA'),
  ('./res/note_icons/3.png', './res/note_icons/3.png', 'DATA'),
  ('./res/note_icons/4.png', './res/note_icons/4.png', 'DATA'),
  ('./res/note_icons/5.png', './res/note_icons/5.png', 'DATA'),
  ('./res/note_icons/6.png', './res/note_icons/6.png', 'DATA'),
  ('./res/note_icons/7.png', './res/note_icons/7.png', 'DATA'),
  ('./res/note_icons/8.png', './res/note_icons/8.png', 'DATA'),
  ('./res/note_icons/9.png', './res/note_icons/9.png', 'DATA'),
  ('./res/note_icons/note_combat.png', './res/note_icons/note_combat.png', 'DATA'),
  ('./res/note_icons/note_general.png', './res/note_icons/note_general.png', 'DATA'),
  ('./res/note_icons/note_hidden.png', './res/note_icons/note_hidden.png', 'DATA'),
  ('./res/note_icons/note_treasure.png', './res/note_icons/note_treasure.png', 'DATA'),
  ('./res/note_icons/combat_mouseover.png', './res/note_icons/combat_mouseover.png', 'DATA'),
  ('./res/note_icons/general_mouseover.png', './res/note_icons/general_mouseover.png', 'DATA'),
  ('./res/note_icons/hidden_mouseover.png', './res/note_icons/hidden_mouseover.png', 'DATA'),
  ('./res/note_icons/treasure_mouseover.png', './res/note_icons/treasure_mouseover.png', 'DATA'),
  ('./res/note_icons/combat_selected.png', './res/note_icons/combat_selected.png', 'DATA'),
  ('./res/note_icons/general_selected.png', './res/note_icons/general_selected.png', 'DATA'),
  ('./res/note_icons/hidden_selected.png', './res/note_icons/hidden_selected.png', 'DATA'),
  ('./res/note_icons/treasure_selected.png', './res/note_icons/treasure_selected.png', 'DATA')]
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='EMMain',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          icon='res/Icon.icns')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='EMMain')
app = BUNDLE(coll,
             name='EncounterMapper.app',
             icon='res/Icon.icns',
             bundle_identifier=None)
