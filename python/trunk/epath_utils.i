/*      -*- linux-c -*-
 *
 * (C) Copyright IBM Corp. 2003, 2006
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. This
 * file and program are licensed under a BSD style license. See
 * the Copying file included with the OpenHPI distribution for
 * full licensing terms.
 *
 * Author(s):
 *      Steve Sherman <stevees@us.ibm.com>
 *      Renier Morales <renierm@users.sf.net>
 */

#ifndef __EPATH_UTILS_H
#define __EPATH_UTILS_H

#include <glib.h>
#include <SaHpi.h>

#ifdef __cplusplus
extern "C" {
#endif

SaHpiBoolT oh_cmp_ep(const SaHpiEntityPathT *ep1,
		     const SaHpiEntityPathT *ep2);

SaErrorT oh_concat_ep(SaHpiEntityPathT *dest,
		      const SaHpiEntityPathT *append);

SaErrorT oh_decode_entitypath(const SaHpiEntityPathT *ep,
			      oh_big_textbuffer *bigbuf);

SaErrorT oh_encode_entitypath(const char *epstr,
			      SaHpiEntityPathT *ep);

SaErrorT oh_init_ep(SaHpiEntityPathT *ep);

SaErrorT oh_fprint_ep(FILE *stream, const SaHpiEntityPathT *ep, int offsets);
SaErrorT oh_print_ep(const SaHpiEntityPathT *ep, int offsets);

SaErrorT oh_set_ep_location(SaHpiEntityPathT *ep,
			    SaHpiEntityTypeT et,
			    SaHpiEntityLocationT ei);

SaHpiBoolT oh_valid_ep(const SaHpiEntityPathT *ep);

char * oh_derive_string(SaHpiEntityPathT *ep,
			 SaHpiEntityLocationT offset,
			 int base,
			 const char *str);

#ifdef __cplusplus
}
#endif

#endif

