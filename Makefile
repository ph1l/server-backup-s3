PREFIX  := $(DESTDIR)/usr/local
BIN_DIR := $(PREFIX)/bin
LIB_DIR := $(PREFIX)/lib

%: %.in
	sed -e 's|@@LIB_DIR@@|$(LIB_DIR)|' $< > $@

all: libbackup.bash libbackup-lvm.bash server-backup-s3 lvm-snapshot-backup-s3

install: all
	install -g root -o root -m 0644 \
		libbackup.bash $(LIB_DIR)/libbackup.bash
	install -g root -o root -m 0644 \
		libbackup-lvm.bash $(LIB_DIR)/libbackup-lvm.bash
	install -g root -o root -m 0755 \
		server-backup-s3 $(BIN_DIR)/server-backup-s3
	install -g root -o root -m 0755 \
		lvm-snapshot-backup-s3 $(BIN_DIR)/lvm-snapshot-backup-s3

clean:
	rm -f server-backup-s3 lvm-snapshot-backup-s3
