from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from .utils import create_dataFrame , convert_to_float , calc_call

from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

class DashboardHome( View):
    template_name = "dashboard.html"
    #redirect_field_name = '/profile/login'
    def get(self, request,*args, **kwargs):
        x , y ,lastUpdate =create_dataFrame()
        x = convert_to_float(x)
        y = convert_to_float(y)
        call_list_data = []
        
        for index, row in x.iterrows():
            
            data = []
            dict_temp = {}
            for col in row:
                data.append(col)

            dict_temp = {index: data}
            call_list_data.append(dict_temp)
            
        call_header_table = x.columns
        put_list_data = []
        for index, row in y.iterrows():
            
            data = []
            dict_temp = {}
            for col in row:
                data.append(col)

            dict_temp = {index: reversed(data)}
            put_list_data.append(dict_temp)
        
        put_header_table = []
        for i in reversed(y.columns):
            put_header_table.append(i) 
            
        dr = calc_call(x)
        
        dr_list_data = []
        
        for index, row in dr.iterrows():
            
            data = []
            dict_temp = {}
            for col in row:
                data.append(col)

            dict_temp = {index: data}
            dr_list_data.append(dict_temp)
            
        dr_header_table = dr.columns
        context = {'x':x, 'call_header_table':call_header_table  ,'call_list_data':call_list_data , 'put_header_table':put_header_table , 'put_list_data':put_list_data , 'dr_header_table':dr_header_table , 'dr_list_data': dr_list_data, 'lastUpdate' : lastUpdate}
        return render(request,self.template_name ,context)