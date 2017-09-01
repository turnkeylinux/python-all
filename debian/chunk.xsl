<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
		xmlns:xhtml="http://www.w3.org/1999/xhtml"
		exclude-result-prefixes="xhtml"
                version="1.0">
  <xsl:import
    href="http://docbook.sourceforge.net/release/xsl/current/xhtml/chunk.xsl"/>
  <xsl:output method="html" encoding="utf-8" indent="yes"/>
  <xsl:param name="chunk.first.sections">1</xsl:param>
  <xsl:param name="chunk.section.depth">0</xsl:param>
  <xsl:param name="generate.section.toc.level">1</xsl:param>
  <xsl:param name="section.autolabel">1</xsl:param>
  <xsl:param name="section.label.includes.component.label">1</xsl:param>
  <xsl:param name="ulink.target">_blank</xsl:param>
  <xsl:param name="use.id.as.filename">1</xsl:param>
</xsl:stylesheet>
