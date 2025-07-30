#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""\
* *[Summary]* :: marmeSendExample.py -- A basic mail sending script That uses marmeSendLib and msgOut

Relevant Command Lines:

marmeSendExample.py  # Logging and Tracing are not enabled
marmeSendExample.py -v 1 --runMode runDebug
marmeSendExample.py -v 20 --runMode dryRun
"""

from bisos import b
from bisos.b import cs
from bisos.b import b_io


import sys

import email

from email.mime.text import MIMEText
#from email.mime.application import MIMEApplication
#from email.mime.multipart import MIMEMultipart
#from email.MIMEBase import MIMEBase
#from email import Encoders



# from bisos.marmee import marmeAcctsLib
#
from bisos.marmee import x822Out
from bisos.marmee import marmeeSendLib

from bisos.marmee import marmeeTrackingLib

def curGet_bxoId(): return "mcm"
def curGet_sr(): return "marme/dsnProc"

fromLine="from@example.com"
toLine="to@example.com"
envelopeLine="envelope@example.com"

def mailSendingExample():


    bxoId = curGet_bxoId()
    sr = curGet_sr()

    sendingMethod = x822Out.SendingMethod.submit

    msg = email.message.Message()  #msg = MIMEText() # MIMEMultipart() 

    msg['From'] = fromLine
    msg['To'] = toLine

    msg['Subject'] = """Example Of A Simple And Tracked Message"""

    envelopeAddr = envelopeLine

    if x822Out.sendingMethodSet(msg, sendingMethod).isProblematic():
        return x822Out.sendingMethodSet(msg, sendingMethod)
        
    msg.add_header('Content-Type', 'text')
    msg.set_payload(
    """ 
This is a simple example message with a simple attachment
being sent using the current enabled controlledProfile and mailAcct.

On the sending end, use mailAcctsManage.py with 
-i enabledControlProfileSet and -i enabledMailAcctSet
to select the outgoing profile. The current settings are:
    ControlProfile={controlProfile}  -- MailAcct={mailAcct}

This message is then submitted for sending with sendCompleteMessage().cmnd(msg)

    """.format(
        controlProfile=marmeAcctsLib.enabledControlProfileObtain(
            curGet_bxoId(),
            curGet_sr(),
        ),
        mailAcct=marmeAcctsLib.enabledInMailAcctObtain(
            curGet_bxoId(),
            curGet_sr(),
        )
    ))


    #
    ###########################
    #
    # Above is the real content of the email.
    #
    # We now augment the message with:
    #   - explicit envelope address -- To be used for Delivery-Status-Notifications (DSN)
    #   - The email is to be tagged for crossReferencing when DSN is received (e.g. with peepid)    
    #   - Request that non-delivery-reports be acted upon and sent to co-recipients
    #   - Explicit delivery-reports are requested
    #   - Explicit read-receipts are requested
    #   - Injection/Submission parameters are specified
    # The message is then sent out
    #

    x822Out.envelopeAddrSet(
        msg,
        mailBoxAddr=envelopeAddr,  # Mandatory
    )

    #
    # e.g., peepId will be used to crossRef StatusNotifications
    #
    x822Out.crossRefInfo(
        msg,
        crossRefInfo="XrefForStatusNotifications"  # Mandatory
    )

    #
    # Delivery Status Notifications will be sent to notifyTo=envelopeAddr
    #
    x822Out.nonDeliveryNotificationRequetsForTo(
        msg,
        notifyTo=envelopeAddr,
    )

    #
    # In case of Non-Delivery, coRecipientsList will be informed
    #
    x822Out.nonDeliveryNotificationActions(
        msg,
        coRecipientsList=[toLine],        
    )

    #
    # Explicit Delivery Report is requested
    #
    x822Out.deliveryNotificationRequetsForTo(
        msg,
        recipientsList=[toLine],
        notifyTo=envelopeAddr,
    )

    #
    # Explicit Read Receipt is requested
    #    
    x822Out.dispositionNotificationRequetsForTo(
        msg,
        recipientsList=[toLine],        
        notifyTo=envelopeAddr,
    )

    if x822Out.sendingMethodSet(msg, sendingMethod).isProblematic():
        return b_io.eh.badLastOutcome()
        
    if not marmeeSendLib.bx822Set_sendWithEnabledAcct(
            msg=msg,
            sendingMethod=sendingMethod,
            bxoId=bxoId,
            sr=sr,
    ):
        return b_io.eh.badOutcome()

    marmeeTrackingLib.deliveryEvent_injectBefore(
        bxoId,
        sr,
        msg,
    )

    cmndOutcome = marmeeSendLib.sendCompleteMessage().cmnd(
        interactive=False,
        msg=msg,
        bxoId=bxoId,
        sr=sr,
    )

    marmeeTrackingLib.deliveryEvent_injectAfter(
        bxoId,
        sr,
        msg,
    )
        
    return cmndOutcome


def main():
    #
    # ICM Library Setup Begins
    #
    
    icmRunArgs, icmArgsParser = cs.G_argsProc(
        arguments=sys.argv,
        extraArgs=None,
    )
    
    # logControler = b_io.log.Control()
    # logControler.loggerSet(icmRunArgs)

    G = cs.globalContext.get()
    G.globalContextSet( icmRunArgs=icmRunArgs )

    #
    # ICM Library Setup Begins
    #
   
    mailSendingExample()

     
if __name__ == "__main__":
    main()
    
