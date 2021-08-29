sc_path = $(SCPATH)
src = src
config = default

all: build/patch_rt.mpq maps

run: patch
	@$(sc_path)/StarCraft.exe -launch

run-wine: patch
	@WINEDEBUG=-all wine explorer /desktop=sc,640x480 $(sc_path)/StarCraft.exe -launch

run-wine-adv: patch
	sudo sysctl kernel.randomize_va_space=0 # Disable ASLR so we can enable a hacks easily
	@WINEDEBUG=-all wine explorer /desktop=sc,640x480 $(sc_path)/StarCraft.exe -launch &
	sleep 4
	xdotool search --name Wine windowactivate
	xdotool key s
	sleep .1
	xdotool key e
	sleep .8
	xdotool key alt o
	sleep .8
	xdotool key u
	# We have to patch a running game to get the speed hack, so try in 3 seconds and then 20
	sleep 3
	sudo gdb -batch -command tools/hacks.gdb $(sc_path)StarCraft.exe `pgrep StarCraft.exe`
	sleep 20
	sudo gdb -batch -command tools/hacks.gdb $(sc_path)StarCraft.exe `pgrep StarCraft.exe`

patch: build/patch_rt.mpq maps
	@echo Overwriting existing patch_rt.mpq
	@cp $(sc_path)/patch_rt.mpq $(sc_path)/patch_rt_bak.mpq
	@cp build/patch_rt.mpq $(sc_path)/patch_rt.mpq
	@cp build/*.scx $(sc_path)/Maps

build/patch_rt.mpq: build/aiscript.bin
	@echo Creating MPQ
	@# This effectively replaces a 64050 byte uncompressed aiscript.bin in a patch_rt.mpq file.
	@# The MPQ was split in half leaving a gap that we can just slot our aiscript.bin into.
	@truncate -s 64050 $<
	@cat tools/patch_rt_pre.mpq $< tools/patch_rt_post.mpq > $@

maps: build/aiscript.bin
	@echo Creating Maps
	@truncate -s 64050 build/aiscript.bin
	@python2 tools/eud_write_bin.py

triggers: build/aiscript.bin
	@echo Creating triggers
	@python2 tools/eud_gen_trigs.py

build/aiscript.bin: build/combined.pyai
	@echo Creating script binaries
	@python2 tools/PyAI.pyw --compile --hidewarns ../$< ../$@ ../build/bwscript.bin
	@echo aiscript.bin size:
	@wc -c < $@

build/combined.pyai: build/terran.pyai build/zerg.pyai build/protoss.pyai
	@echo Combining scripts
	@cat $^ src/ums-scripts.pyai > $@

build/%.pyai: src/%
	@echo Building $@ $<
	@cp tools/config_$(config).json tools/config.json
	@node tools/build_ai $(subst src/,,$<) $@;
	@rm tools/config.json

clean:
	@echo Removing old files
	@rm -f build/*.bin
	@rm -f build/*.mpq
	@rm -f build/*.pyai
	@rm -f build/*.trg
	@rm -f build/*.scx