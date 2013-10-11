import smtplib

class EmailSender(object):
    
    def __init__(self):
        pass
    
    def send_email(self, msg, receiver):
        gmail_user = "chengjia.huo@gmail.com"
        gmail_pwd = "No2alive"
        FROM = 'chengjia.huo@gmail.com'
        TO = [receiver] #must be a list
        SUBJECT = "SIDs Alert!!!"
        
        # Prepare actual message
        message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
        """ % (FROM, ", ".join(TO), SUBJECT, msg)
        try:
            #server = smtplib.SMTP(SERVER) 
            server = smtplib.SMTP("smtp.gmail.com", 587) #or port 465 doesn't seem to work!
            server.ehlo()
            server.starttls()
            server.login(gmail_user, gmail_pwd)
            server.sendmail(FROM, TO, message)
            #server.quit()
            server.close()
            print 'successfully sent the mail'
        except:
            print "failed to send mail"
            
if __name__ == "__main__":
    EmailSender().send_email("test\ntest123", 'chengjia.huo@gmail.com')