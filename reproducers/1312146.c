#include <alloca.h>
#include <stdio.h>

#include <sys/uio.h>

#include "systemd/sd-journal.h"

int main() {
    int res;
    // Change 511 to 512 and, using journalctl --reverse --output=verbose
    // 1. Error message: Failed to get source realtime timestamp: Bad message
    // 2. No entry in log.
    int length = 511;
    char my_bytes[511];
    FILE *fp;
    struct iovec * iov;

    fp = fopen("graph.bytes", "rb");
    res = fread(my_bytes, sizeof(char), length, fp); 
    if (res != length) {
        return -30;
    }

    iov = alloca(sizeof(struct iovec));
    iov[0].iov_base = my_bytes;
    iov[0].iov_len = length;
    iov[1].iov_base = "MESSAGE=TESTING BYTES";
    iov[1].iov_len = 21;
    res = sd_journal_sendv(iov, 2);
    return res;
}
