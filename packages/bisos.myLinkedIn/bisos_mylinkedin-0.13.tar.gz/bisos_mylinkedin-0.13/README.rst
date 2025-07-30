====================================================================
bisos.myLinkedIn: Your Connections as vCards for Outside of LinkedIn
====================================================================

.. contents::
   :depth: 3
..

Overview
========

*bisos.myLinkedIn* takes contents of
Basic\ :sub:`LinkedInDataExport`.zip and converts them to vCards for
your connections and then augments them with the *Contact info* of your
first-level connections. The purpose of *bisos.myLinkedIn* is to
facilitate convenient communication with your first-level connections
**outside LinkedIn**. *bisos.myLinkedIn* is structured as two layers.

-  *Layer 1* – myLinkedIn-Basic – **myLinkedIn.cs** – Operates purely on
   the content of Basic\ :sub:`LinkedInDataExport`.zip. Connections.csv
   is used to create vCards for each of your connections.
   Invitations.csv is then used to augment the vCards. Messages.csv is
   converted to Maildir format for reading using your own MUA (Mail User
   Agent). The email address (and other contact info) of only about
   one-fourth of your first-level connections is in Connections.csv. The
   use of Layer 1 does not violate LinkedIn policies in any way.

-  *Layer 2* – myLinkedIn-Plus – **myLinkedinWeb.cs** – Uses *layer 1*
   and enriches it with the *Contact info* for each of the vCards. The
   email address (and other contact info) of most of your first-level
   connections is not available in *layer 1*. **myLinkedInWeb.cs** goes
   to your first-level connections' home page, clicks on the *Contact
   info*, obtains email and other contact info from the web, and adds it
   to the vCards. Some may say that the use of Layer 2 does violate
   LinkedIn policies. I don't think so. In my view, what
   **myLinkedInWeb.cs** does falls in the category of fair and
   reasonable use. I have been on LinkedIn for more than 20 years, and I
   expect to have convenient access to the *Contact info* of my
   connections. If LinkedIn considers this use unacceptable, then it
   should include the *Contact info* of **ALL** of my connections in
   Basic\ :sub:`LinkedInDataExport`.zip. Does LinkedIn really expect me
   to keep my vCards current manually?

*bisos.myLinkedIn* is a python package that uses the
`PyCS-Framework <https://github.com/bisos-pip/pycs>`__. It is a
BISOS-Capability and a Standalone-BISOS-Package.

The *bisos.linkedin* package automates the process of transforming
LinkedIn export data (.csv) into enriched vCards (.vcf), specifically
focusing on the first-level connections present in your LinkedIn data.
LinkedIn’s export includes valuable information about your
connections—such as names, job titles, company details, and
invitations—that naturally fits into a contact management system like
vCards. However, contact info (email, phone, etc.) of most connections
is not included in the Basic\ :sub:`LinkedInDataExport`.zip file. By
leveraging this package, you can convert, enrich, and augment these
details into vCards that are readily importable into your preferred
usage environment (e.g., Emacs ebdb, MS Outlook Contacts, Google
Contacts, or any other vCard-compatible system). This process is
repeatable and scalable, making it easier to maintain an up-to-date
contact database, effectively integrating LinkedIn connection data into
your daily workflow.

Other than adding the *Contact info* of your first-level connections to
the vCards, the *bisos.myLinkedIn* package does not support any form of
web scraping.

Package Documentation At Github
===============================

The information below is a subset of the full of documentation for this
bisos-pip package. More complete documentation is available at:
https://github.com/bisos-pip/capability-cs

.. _table-of-contents:

Table of Contents TOC
=====================

-  `Overview <#overview>`__
-  `Package Documentation At
   Github <#package-documentation-at-github>`__
-  `A Standalone Command-Services PyCS Facility of
   BISOS <#a-standalone-command-services-pycs-facility-of-bisos>`__
-  `Inputs <#inputs>`__

   -  `Layer-1 – myLinkedIn-Basic –
      Basic\ LinkedInDataExport.zip <#layer-1----mylinkedin-basic----basic_linkedindataexportzip>`__
   -  `Layer-2 – myLinkedIn-Plus – Web Connect
      Info <#layer-2----mylinkedin-plus----web-connect-info>`__

-  `Outpts <#outpts>`__

   -  `VCards <#vcards>`__
   -  `Maildirs <#maildirs>`__

-  `Layer-1 – myLinkedIn-Basic – myLinkedIn.cs – Diagram and
   Software–Diagram
   Mapping <#layer-1----mylinkedin-basic----mylinkedincs----diagram-and-softwarediagram-mapping>`__

   -  `Key Features of Layer-1 –
      myLinkedIn.cs <#key-features-of-layer-1----mylinkedincs>`__

-  `Layer-2 – myLinkedIn-Plus – myLinkedInWeb.cs – Diagram and
   Software–Diagram
   Mapping <#layer-2----mylinkedin-plus----mylinkedinwebcs----diagram-and-softwarediagram-mapping>`__

   -  `Key Features of Layer-2 –
      myLinkedInWeb.cs <#key-features-of-layer-2----mylinkedinwebcs>`__

-  `Broader Common Uses – Overview and
   Diagram <#broader-common-uses----overview-and-diagram>`__
-  `Benefits – Distinct and
   Different <#benefits----distinct-and-different>`__
-  `Installation <#installation>`__

   -  `Installation With pipx <#installation-with-pipx>`__
   -  `Installation With pip <#installation-with-pip>`__

-  `Layer-1 Usage <#layer-1-usage>`__

   -  `Obtaining Your
      Basic\ LinkedInDataExport.zip <#obtaining-your-basic_linkedindataexportzip>`__
   -  `FullUpdate in the ~/Downloads
      Directory <#fullupdate-in-the-downloads-directory>`__
   -  `Move Basic\ LinkedInDataExport.zip next to VCards
      Base <#move-basic_linkedindataexportzip-next-to-vcards-base>`__
   -  `Prepare the vCards Base <#prepare-the-vcards-base>`__
   -  `Generate Initial vCards <#generate-initial-vcards>`__
   -  `Augment vCards With
      Invitation <#augment-vcards-with-invitation>`__
   -  `Create Maildir from
      messages.csv <#create-maildir-from-messagescsv>`__

-  `Layer-2 Usage <#layer-2-usage>`__

   -  `Short Comings of Layer-1 <#short-comings-of-layer-1>`__
   -  `Warnings About Use of myLinkedInWeb.cs (Layer-2)
      Software <#warnings-about-use-of-mylinkedinwebcs-layer-2-software>`__
   -  `Running Layer-2 (myLinkedInWeb.cs) on a Handfull of Connections
      LinkedInIds <#running-layer-2-mylinkedinwebcs-on-a-handfull-of-connections-linkedinids>`__
   -  `Running Layer-2 (myLinkedInWeb.cs) on Many or All of Your
      Connections
      LinkedInIds <#running-layer-2-mylinkedinwebcs-on-many-or-all-of-your-connections-linkedinids>`__
   -  `Our Connections Contact Info Are For
      Us <#our-connections-contact-info-are-for-us>`__

-  `Documentation and Blee-Panels <#documentation-and-blee-panels>`__

   -  `bisos.myLinkedIn Blee-Panels <#bisosmylinkedin-blee-panels>`__

-  `Support <#support>`__
-  `Credits <#credits>`__

A Standalone Command-Services PyCS Facility of BISOS
====================================================

Layered on top of Debian, **BISOS** (By\* Internet Services Operating
System) is a unified and universal framework for developing both
internet services and software-service continuums that use internet
services. PyCS (Python Command-Services) of BISOS is a framework that
converges development of CLI and Services. See the `Nature of
Polyexistentials <https://github.com/bxplpc/120033>`__ book for
additional information.

bisos.myLinkedIn is a standalone piece of BISOS. It can be used as a
self-contained Python package separate from BISOS.

Inputs
======

Inputs of myLinkedin-Basic are the .csv files that LinkedIn exports.
Inputs of myLinkedin-Plus are the contact info of your connections which
are web scraped.

Layer-1 – myLinkedIn-Basic – Basic\ :sub:`LinkedInDataExport`.zip
-----------------------------------------------------------------

-  **Connections.csv**: The basic connection data, including LinkedIn
   ID, profile URL, name, etc.
-  **Invitations.csv**: Captures whether you invited the connection or
   were invited, along with the invitation text.
-  **Messages.csv**: Adds LinkedIn message history between you and your
   connections, showing the conversation details and direction.

Layer-2 – myLinkedIn-Plus – Web Connect Info
--------------------------------------------

-  email
-  websites
-  phones

Outpts
======

Outputs of the myLinkedIn package are a set of vCards and Maildirs.

VCards
------

**Connections.csv** and **Invitations.csv** inputs and Web Connect Info
are transformed into a series of vCards (.vcf) – one for each
connection.

Maildirs
--------

**Messages.csv** is converted into Maildir format.

Layer-1 – myLinkedIn-Basic – **myLinkedIn.cs** – Diagram and Software–Diagram Mapping
=====================================================================================

The figure above provides an overview of Layer-1.

A brief description of the nodes is provided below.

+-----------------+------------------------+------------------------+
| Diagram Node    | Software               | Description            |
|                 | Component/Class        |                        |
+=================+========================+========================+
| LinkedIn        | Data Source (LinkedIn) | Origin of all LinkedIn |
|                 |                        | user data              |
+-----------------+------------------------+------------------------+
| Export.zip      | Raw Input              | Downloaded export ZIP  |
|                 |                        | file from LinkedIn     |
+-----------------+------------------------+------------------------+
| ExportedData    | Unzipped Data          | Directory containing   |
|                 | Directory              | CSV and JSON files     |
+-----------------+------------------------+------------------------+
| Connections.csv | LinkedInConnections    | Parses first-level     |
|                 |                        | connections            |
+-----------------+------------------------+------------------------+
| Invitations.csv | LinkedInInvitations    | Parses sent and        |
|                 |                        | received invitations   |
+-----------------+------------------------+------------------------+
| VCard           | VCardUtils / Core      | Base vCards from       |
|                 | Output                 | LinkedIn data          |
+-----------------+------------------------+------------------------+
| Messages.csv    | LinkedInMessages       | Parses message         |
|                 |                        | exchanges with         |
|                 |                        | connections            |
+-----------------+------------------------+------------------------+
| Maildir         | messages               | Enriched vCards with   |
|                 |                        | remote and external    |
|                 |                        | information            |
+-----------------+------------------------+------------------------+

Key Features of Layer-1 – myLinkedIn.cs
---------------------------------------

The \`bisos.myLinkedIn\` Layer-1 Python package provides a set of
utilities for creating a set of vCards for your first-level LinkedIn
connections based on the **Basic\ LinkedInDataExport**. It creates rich
representations of your LinkedIn network in vCard (.vcf) format.

-  VCard Creation:

   Based on data from \`Connections.csv`, a vCard is created for each
   contact. This vCard will then be augmented and enriched.

-  VCard Local Augmentation:

   Augments vCards with data from \`Invitations.csv`. For each contact,
   the invitation status is captured (whether you invited the connection
   or vice versa) and the invitation message text is added to the vCard.

-  Maildir Conversion:

   With data from \`Messages.csv`, Maildirs are created. Conversation
   details are added from **Messages.csv**, organizing the messages in
   chronological order with sender information.

Layer-2 – myLinkedIn-Plus – **myLinkedInWeb.cs** – Diagram and Software–Diagram Mapping
=======================================================================================

The figure above provides an overview of Layer-2. Layer-2 builds on
Layer-1 by enriching the vCards with the information obtained from the
*Contact Info* for each vCard.

A brief description of the relevant nodes is provided below.

+--------------+--------------------------+--------------------------+
| Diagram Node | Software Component/Class | Description              |
+==============+==========================+==========================+
| ContactInfo  | Remote Augmentation      | Scraped contact details  |
|              | Logic                    | from LinkedIn website    |
+--------------+--------------------------+--------------------------+
| VCard        | VCardUtils / Core Output | Base vCards from         |
|              |                          | LinkedIn data            |
+--------------+--------------------------+--------------------------+

Key Features of Layer-2 – myLinkedInWeb.cs
------------------------------------------

Layer-2 (myLinkedIn-Plus) is about remote enrichment of Layer-1
(myLinkedIn-Basic) vCard.

-  Web Contact Info Retrieval:

Extracts additional details from LinkedIn's Contact Info page via
automated scraping, such as email addresses, phone numbers, and other
publicly available contact information.

-  Addition of Contact Info to Local vCard:

Broader Common Uses – Overview and Diagram
==========================================

The figure above provides an overview of how MyLinkedIn (Layers-1 and
Layer-2) are commonly used.

A brief description of the relevant nodes is provided below.

+--------------+--------------------------+--------------------------+
| Diagram Node | Software Component/Class | Description              |
+==============+==========================+==========================+
| External     | User-supplied Sources    | Any third-party or       |
|              |                          | user-maintained source   |
|              |                          | of data                  |
+--------------+--------------------------+--------------------------+
| ExternalInfo | External Data Processor  | Prepares and aligns      |
|              |                          | external info for        |
|              |                          | enrichment               |
+--------------+--------------------------+--------------------------+
| VCard        | VCardUtils / Core Output | Base vCards from         |
|              |                          | LinkedIn data            |
+--------------+--------------------------+--------------------------+
| VCardPlus    | VCardAugmentor           | Enriched vCards with     |
|              |                          | remote and external      |
|              |                          | information              |
+--------------+--------------------------+--------------------------+

-  Seamless Repeatable VCard Generation and Re-Generation:

   The tool automatically converts your first-level LinkedIn connections
   into individual vCard files, using the unique LinkedIn ID as the file
   name. Periodically, you re-generate these.

-  External Augmentation: Optionally integrates with external services
   for contact enrichment to further enhance your vCards with data such
   as job titles, company names, and social profiles.

-  Output vCards are ready for import into other systems (e.g., address
   books, contacts app, Outlook, ebdb).

-  With LinkedIn vCards addresses now in your address book, you can now
   use MTDT (Mail Templating and Distribution and Tracking) to engage in
   mass communications with your LinkedIn connections through email
   (outside of LinkedIn).

Benefits – Distinct and Different
=================================

Open-Source, Self-Hosted Solution: This package offers a self-hosted,
open-source solution that gives users complete control over their
LinkedIn data and privacy, without relying on third-party SaaS
platforms.

This holistic, self-contained solution for augmenting LinkedIn data with
multiple sources and outputting it in a standardized vCard format makes
our approach unique in the landscape of LinkedIn data tools.

Installation
============

The sources for the bisos.myLinkedIn pip package are maintained at:
https://github.com/bisos-pip/linkedinVcard.

The bisos.myLinkedIn pip package is available at PYPI as
https://pypi.org/project/bisos.myLinkedIn

You can install bisos.myLinkedIn with pipx or pip.

Installation With pipx
----------------------

If you only need access to bisos.myLinkedIn on the command line, you can
install it with pipx:

.. code:: bash

   pipx install bisos.myLinkedIn

The following commands are made available:

-  myLinkedIn.cs
-  myLinkedInWeb.cs

Installation With pip
---------------------

If you need access to bisos.myLinkedIn as a Python module, you can
install it with pip:

.. code:: bash

   pip install bisos.myLinkedIn

Layer-1 Usage
=============

.. code:: bash

   bin/myLinkedIn.cs

Obtaining Your Basic\ :sub:`LinkedInDataExport`.zip
---------------------------------------------------

As of 2025-06-10 Tue 11:35, you can obtain a snapshot of your current
connections data by following these steps:

-  1) Access Settings & Privacy: Click the "Me" icon (usually your
   profile picture) at the top of the LinkedIn homepage, then select
   "Settings & Privacy" from the dropdown menu.

-  2) Go to Data Privacy: On the left side of the Settings & Privacy
   page, click "Data privacy".

-  3) Initiate Data Download: Under the "How LinkedIn uses your data"
   section, click "Get a copy of your data".

-  4) Select Data & Request Archive: You'll be presented with options to
   download specific data or a larger data archive.

   -  For a complete backup, choose "Download larger data archive…".
   -  To select specific data categories, click "Want something in
      particular?" and choose the files you want.
   -  After making your selection, click "Request archive".

-  5) Download the Archive: LinkedIn will send an email to your primary
   email address when the data is ready for download.

   -  You'll have a limited time to download the file (typically 72
      hours).
   -  Click the download link in the email or return to the "Download
      your data" section in your Settings & Privacy to download the .zip
      file. ￼

FullUpdate in the ~/Downloads Directory
---------------------------------------

Run:

.. code:: bash

   myLinkedIn.cs --myLinkedInBase="~/Downloads"  -i fullUpdate ~/Downloads/Basic_LinkedInDataExport.zip

You can then import the vCards in ~/Downloads/VCards to your usage
environment (Outlook, Google Contacts).

Move Basic\ :sub:`LinkedInDataExport`.zip next to VCards Base
-------------------------------------------------------------

In BISOS, it is typically at:
**~/bpos/usageEnvs/selected/myLinkedIn/selected**. You can choose any
location for the base.

Prepare the vCards Base
-----------------------

Run:

.. code:: bash

   myLinkedIn.cs  -i exportedPrep ~/bpos/usageEnvs/selected/myLinkedIn/selected/Basic_LinkedInDataExport.zip

Generate Initial vCards
-----------------------

Run:

.. code:: bash

   myLinkedIn.cs --vcardsDir="~/bpos/usageEnvs/selected/myLinkedIn/selected/VCards"  -i vcardsGenerate ~/bpos/usageEnvs/selected/myLinkedIn/selected/LinkedInDataExport/Connections.csv

Augment vCards With Invitation
------------------------------

Run:

.. code:: bash

   myLinkedIn.cs --vcardsDir="~/bpos/usageEnvs/selected/myLinkedIn/selected/VCards"  -i vcardsInvitations ~/bpos/usageEnvs/selected/myLinkedIn/selected/LinkedInDataExport/Invitations.csv

Create Maildir from messages.csv
--------------------------------

Run:

.. code:: bash

   myLinkedIn.cs --maildir="~/bpos/usageEnvs/selected/myLinkedIn/selected/maildir"  -i maildirMessages ~/bpos/usageEnvs/selected/myLinkedIn/selected/LinkedInDataExport/messages.csv

Layer-2 Usage
=============

.. code:: bash

   bin/myLinkedInWeb.cs

Short Comings of Layer-1
------------------------

Most of the vCards generated in Layer-1 do not include contact
information of your connections. You can go to the home page of each of
your connections, click on their *Contact info* button and see their
email address and their other contact info.

So, this information (contact info of ALL of your connections is
available to you), but Microsoft-LinkedIn has chosen not to supply that
information to you.

Furthermore, Microsoft-LinkedIn prohibits the use of automated tools to
extract your own connection's non-LinkedIn related contact info.
Microsoft-LinkedIn says: "To protect our members’ privacy and help
foster authentic interactions on LinkedIn, our User Agreement prohibits
the use of these tools." But look, my connection's contact info includes
his/her email address which is for outside of LinkedIn interactions. My
connection's contact info includes his/her phone number which is for
outside of LinkedIn interactions. Accessing this complete information in
no way, shape, or form impacts "authentic interactions on LinkedIn". So,
the Microsoft-LinkedIn policy of not allowing me to automate access to
my own connections' contact info is bogus. Microsoft-LinkedIn wants to
lock me inside of LinkedIn and use Microsoft-LinkedIn's messaging
service instead of email outside of LinkedIn.

I consider using automated tools to obtain ALL of my own connections'
contact info as fair and reasonable use. It is the Microsoft-LinkedIn
User Agreement that is unreasonable.

Layer-2 overcomes this shortcoming of Layer-1. It automates the addition
of ALL of your connections' contact info to their vCards of Layer-1.

After being temporarily restricted for having used Layer-2, I presented
the above logic to Microsoft-LinkedIn and requested clarification. They
have not responded to me. But, they removed the temporary restriction. I
have almost ALL of my connections' contact info and I am back on
LinkedIn. A complete record of all my communications with
Microsoft-LinkedIn with regard to Layer-2 usage is in
`file:./linkedIn.com-transcript/README.org <./linkedIn.com-transcript/README.org>`__

Warnings About Use of myLinkedInWeb.cs (Layer-2) Software
---------------------------------------------------------

myLinkedIn package's Layer-2 software is a web automation tool (a web
scraper) limited to a very narrow scope of information gathering. Yet,
Microsoft-LinkedIn may consider such use as in violation of their User
Agreement, and your access to LinkedIn may be restricted.

myLinkedIn package's Layer-2 software comes AS IS with no warranties of
any sort. If you use it, you are on your own. If you get banned, it is
not my fault or the software's fault.

Running Layer-2 (myLinkedInWeb.cs) on a Handfull of Connections LinkedInIds
---------------------------------------------------------------------------

**myLinkedInWeb.cs -i contactInfoToVCard** takes its input as a list of
inputs as arguments or on stdin. The inputs can be LinkedInIds or path
to a LinkedIn vCard.

At this time, only Chrome is supported. Make sure that Chrome is not
running when you run **myLinkedInWeb.cs -i contactInfoToVCard**.

To run contactInfoToVCard on just a couple of LinkedInIds, try:

.. code:: bash

   ls ~/bpos/usageEnvs/selected/myLinkedIn/selected/VCards/* | myLinkedInWeb.cs -i vcardNeedsUpdate | head -2 |  myLinkedInWeb.cs --account="someUser" --password="somePasswd"  -i contactInfoToVCard

The account and password are your LinkedIn credentials. If you are
already logged-in at LinkedIn, account and password are not needed and
are not used.

Running Layer-2 (myLinkedInWeb.cs) on Many or All of Your Connections LinkedInIds
---------------------------------------------------------------------------------

Once you have successfully run it on a handful, run it in batches of say
50, or all at once.

To run contactInfoToVCard on say 50 of (head -50) the LinkedInIds, try:

.. code:: bash

   ls ~/bpos/usageEnvs/selected/myLinkedIn/selected/VCards/* | myLinkedInWeb.cs -i vcardNeedsUpdate | head -50 |  myLinkedInWeb.cs --account="someUser" --password="somePasswd"  -i contactInfoToVCard

Our Connections Contact Info Are For Us
---------------------------------------

I added my contact info to my profile, so that my connections can
contact me. My connections have done the same for me. It is not for
Microsoft-LinkedIn to say that I cannot conveniently access all of that
information.

Documentation and Blee-Panels
=============================

bisos.myLinkedIn is part of the ByStar Digital Ecosystem
http://www.by-star.net.

This module's primary documentation is in the form of Blee-Panels.
Additional information is also available in:
http://www.by-star.net/PLPC/180047

bisos.myLinkedIn Blee-Panels
----------------------------

bisos.myLinkedIn Blee-Panels are in the ./panels directory. From within
Blee and BISOS, these panels are accessible under the Blee "Panels"
menu.

See
`file:./panels/_nodeBase_/fullUsagePanel-en.org <./panels/_nodeBase_/fullUsagePanel-en.org>`__
for a starting point.

Support
=======

| For support, criticism, comments, and questions, please contact the
  author/maintainer
| `Mohsen Banan <http://mohsen.1.banan.byname.net>`__ at:
  http://mohsen.1.banan.byname.net/contact

Credits
=======

ChatGPT initial implementation is at: myLinkedIn/chatgpt
