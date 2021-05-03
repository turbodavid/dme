<html>
    <head>
    </head>
    <body>
      %for o in objects :
      	<% setLang(user.lang) %>
		    <div class="DivWordWrap Centrar Ancho1000">
		    	<table>
						<tr>
							<td colspan="2">
								<table>
									<tr>
										<td>
											<br>
										</td>
										<td style="width: 865px;" align="right">
											<table>
												<tr>
													<td style="font-family: Arial, Helvetica, sans-serif; font-size: 8pt; font-weight: bold; text-align: left;">
														<br>
													</td>
												</tr>
												<tr>
													<td style="font-family: Arial, Helvetica, sans-serif; font-size: 8pt; text-align: left;">
														${ date_to_text(o.date) }
													</td>
												</tr>
												<tr>
													<td style="width: 250px;">
														<br>
													</td>
												</tr>
											</table>
										</td>
									</tr>
								</table>
							</td>
						</tr>
						<tr>
							<td style="width: 10px;">
								<br>
							</td>
							<td>
								<table>
									<tr>
										<td style="font-family: Arial, Helvetica, sans-serif; font-size: 8pt; font-weight: bold; text-align: left; width: 580px;">
											${get_name_beneficiary(get_id_beneficiary)}
										</td>
										<td style="width: 15px;">
										</td>
										<td style="font-family: Arial, Helvetica, sans-serif; font-size: 8pt; text-align: right;">
											${ o.amount }
										</td>
									</tr>
									<tr>
										<td style="font-family: Arial, Helvetica, sans-serif; font-size: 8pt; text-align: left; width: 580px;">
											<p>
												${ convert_to_words(o) }
											</p>
										</td>
										<td colspan="2">
										</td>
									</tr>
									<tr>
										<td colspan="2" style="height:185px;">
											<table>
												<tr>
													${ legend_payment_beneficiary(o, 'check') }
												</tr>
											</table>
										</td>
									</tr>
								</table>
							</td>
						</tr>
						<tr>
							<td colspan="2" align="right">
								<table>
									<tr>
										<td colspan="2" align="right" style="font-size: 10px;">
											${ o.number }
										</td>
										<td></td>
									</tr>
									<tr>
										<td style="height: 5px;" colspan="2">
										</td>
									</tr>
									<tr>
										<td style="font-family: Arial, Helvetica, sans-serif; font-size: 8pt; text-align: center; width: 200px;" colspan="2">
											${ month_and_day_to_text(o.date) }
										</td>
										<td style="font-family: Arial, Helvetica, sans-serif; font-size: 8pt; text-align: right;">
											${ year_to_text(o.date) }
										</td>
									</tr>
									<tr>
										<td colspan="2" style="width: 20px;">							
										</td>									
									</tr>
									<tr>										
										<td style="font-family: Arial, Helvetica, sans-serif; font-size: 8pt; text-align: center;" colspan="2">		
											${ o.amount }
										</td>
									</tr>
								</table>
							</td>
						</tr>
						<tr>
							<td colspan="2">
								<table>
									<tr>
										<td style="width: 10px;">
										</td>
										<td style="font-family: Arial, Helvetica, sans-serif; font-size: 8pt; font-weight: bold; text-align: left; width:550px;">
											${ o.partner_id.name }
										</td>
										<td>												
										</td>
									</tr>
									<tr>
										<td style="width: 10px;">
											<br>
										</td>
										<td style="font-family: Arial, Helvetica, sans-serif; font-size: 8pt; text-align: left;" colspan="2">
											${ convert_to_words(o) }
										</td>
									</tr>
									<tr>
										<td colspan="2" style="height:135px;">
											<table>
												<tr>
													${ legend_payment_beneficiary(o, 'policy') }
												</tr>
											</table>
										</td>
									</tr>
								</table>
							</td>
						</tr>
						<tr>	
							<td colspan="2">
								<table>
									<tr>
										<td style="font-family: Arial, Helvetica, sans-serif; font-size: 8pt; text-align: left; width: 400px;">
											${ o.name or '' }
										</td>
										<td>
										</td>
									</tr>
								</table>
							</td>
						</tr>
						<tr>
							<td colspan="2">
								<br>
							</td>
						</tr>
						<tr>
							<td colspan="2">
								<table style="height:535px;">
									<tr style="vertical-align: top;">
										<td>
											<table cellspacing="0" celpadding="0" y border="0">
												%for l in get_lines_check(o):
												%if exist_line_parent(l, l.account_id.parent_id.id, 'parent_id', o.id) == 0:
												<tr>
													<td colspan="6">
														<div>
															<table>
																<tr style="vertical-align: top;">
																	<!-- CUENTA -->
																	<td style="font-family: Arial, Helvetica, sans-serif; font-size: 7pt; font-weight: bold; text-align: left; width: 0px;">
																		${ get_lines_parent(l, l.account_id.parent_id.id, 'parent_id', o)}
																	</td>
																	<!-- SUB-CUENTA -->
																	<td style="font-family: Arial, Helvetica, sans-serif; font-size: 7pt; font-weight: bold; text-align: left; width: 140px;">
																		&nbsp;
																	</td>
																	<!-- NOMBRE -->
																	<td style="font-family: Arial, Helvetica, sans-serif; font-size: 7pt; font-weight: bold; text-align: left; width: 450px;">
																		${ get_lines_parent(l, l.account_id.parent_id.id, 'parent_id_name', o)}
																	</td>
																	<!-- PARCIAL -->
																	<td style="font-family: Arial, Helvetica, sans-serif; font-size: 7pt; font-weight: bold; text-align: right; width: 40px;">
																	</td>
																	<!-- DEBE -->
																	<td style="font-family: Arial, Helvetica, sans-serif; font-size: 7pt; font-weight: bold; text-align: right; width: 140px;">
																		${ formatLang(get_lines_parent(l, l.account_id.parent_id.id, 'debit', o))}
																	</td>
																	<!-- HABER -->
																	<td style="font-family: Arial, Helvetica, sans-serif; font-size: 7pt; font-weight: bold; text-align: right; width: 140px;">
																		${ formatLang(get_lines_parent(l, l.account_id.parent_id.id, 'credit', o))}
																	</td>
																</tr>		
															</table>
														</div>
													</td>
												</tr>
												%endif
												%if exist_line_parent(l, l.account_id.id, 'account_id', o.id) == 0:
												<tr style="vertical-align: top;">
													<!-- CUENTA -->
													<td style="font-family: Arial, Helvetica, sans-serif; font-size: 7pt; text-align: center; width: 0px;">
													</td>
													<!-- SUB-CUENTA -->
													<td style="font-family: Arial, Helvetica, sans-serif; font-size: 7pt; text-align: center; width: 100px;">
														${ get_lines_parent(l, l.account_id.id, 'account_id', o)}
													</td>
													<!-- NOMBRE -->
													<td style="font-family: Arial, Helvetica, sans-serif; font-size: 7pt; text-align: left; width: 200px;">
														${ get_lines_parent(l, l.account_id.id, 'name', o)}
													</td>
													<!-- PARCIAL -->
													<td style="font-family: Arial, Helvetica, sans-serif; font-size: 7pt; text-align: right; width: 120px;">
														${ formatLang(get_lines_parent(l, l.account_id.id, 'partial', o))}
													</td>
													<!-- DEBE -->
													<td style="font-family: Arial, Helvetica, sans-serif; font-size: 7pt; text-align: right; width: 120px;">
														&nbsp;
													</td>
													<!-- HABER -->
													<td style="font-family: Arial, Helvetica, sans-serif; font-size: 7pt; text-align: right; width: 120px;">
														&nbsp;
													</td>
												</tr>
												%endif
												%endfor
											</table>
										</td>
									</tr>
								</table>
							</td>
						</tr>
						<tr>
							<td colspan="2">
								<table>
									<tr>
										<td style="width: 100px;">
										</td>
										<td style="font-family: Arial, Helvetica, sans-serif; font-size: 8pt; text-align: left; width: 620px;">
											${ o.number }
										</td>
										<td style="font-family: Arial, Helvetica, sans-serif; font-size: 8pt; text-align: right; width: 110px;">
											${ formatLang(total_amount_debit(o)) }
										</td>
										<td style="font-family: Arial, Helvetica, sans-serif; font-size: 8pt; text-align: right; width: 110px;">
											${ formatLang(total_amount_credit(o)) }
										</td>
									</tr>
									<tr><td><br></td></tr>
									<tr>
										<td style="font-family: Arial, Helvetica, sans-serif; font-size: 7pt; text-align: left;" colspan="4">
											${getCreateUser(o)}						
										</td>
									</tr>
								</table>
							</td>
						</tr>						
					</table>
		    </div>
    	%endfor
    </body>
</html>
