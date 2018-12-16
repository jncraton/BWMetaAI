sc_path = $(SCPATH)
src = src
config = default

all: mpq maps

run: patch
	@$(sc_path)/StarCraft.exe -launch

run-wine: patch
	@WINEDEBUG=-all wine $(sc_path)/StarCraft.exe -launch &
	sleep 4
	xdotool search --name Wine windowactivate
	xdotool key s
	sleep .1
	xdotool key e
	sleep .8
	xdotool key alt o
	sleep .8
	xdotool key u

patch: mpq maps
	@echo Overwriting existing patch_rt.mpq
	@cp $(sc_path)/patch_rt.mpq $(sc_path)/patch_rt_bak.mpq
	@cp build/patch_rt.mpq $(sc_path)/patch_rt.mpq
	@cp build/*.scx $(sc_path)/Maps

mpq: bins
	@echo Creating MPQ
	@# This effectively replaces a 64050 byte uncompressed aiscript.bin in a patch_rt.mpq file.
	@# The MPQ was split in half leaving a gap that we can just slot our aiscript.bin into.
	@truncate -s 64050 build/aiscript.bin
	@cat tools/patch_rt_pre.mpq build/aiscript.bin tools/patch_rt_post.mpq > build/patch_rt.mpq

maps: bins
	@echo Creating Maps
	@truncate -s 64050 build/aiscript.bin
	@python tools/eud_write_bin.py

triggers: bins
	@echo Creating triggers
	@python tools/eud_gen_trigs.py

bins: combined_scripts
	@echo Creating script binaries
	@python tools/PyAI.pyw -c -w ../build/combined.pyai ../build/aiscript.bin ../build/bwscript.bin
	@echo aiscript.bin size:
	@wc -c < build/aiscript.bin

combined_scripts: clean terran.pyai zerg.pyai protoss.pyai
	@echo Combining scripts
	@cat build/terran.pyai build/zerg.pyai build/protoss.pyai > build/combined.pyai

%.pyai:
	@echo Building $@
	@cp tools/config_$(config).json tools/config.json
	@node tools/build_ai $(subst .pyai,,$@) build/$@;
	@rm tools/config.json

clean:
	@echo Removing old files
	@rm -f build/*.bin
	@rm -f build/*.mpq
	@rm -f build/*.pyai
	@rm -f build/*.trg
	@rm -f build/*.scx