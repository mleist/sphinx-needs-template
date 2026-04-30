# linkml/private/

Drop your **private LinkML data** here (e.g. internal stories or
extra schema modules).

To include private data in the build, edit the Makefile so that
`needs-from-linkml` is invoked with your private data directory after the
public one, writing to a separate output prefix.
