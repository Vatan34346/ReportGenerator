import pandas as pd
from django.shortcuts import render
import matplotlib
import matplotlib.pyplot as plt
import io
import urllib,  base64
from .forms import UploadFileForm

matplotlib.use('Agg')

def handle_uploaded_file(file):
    if file.name.endswith('.csv'):
        df = pd.read_csv(file, header=0, skip_blank_lines=True)
    else:
        df = pd.read_excel(file, header=0, skiprows=lambda x: 'Unnamed' in str(x))

    df.columns = df.columns.str.strip()

    return df


def plot_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)

    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)
    plt.close(fig)

    return uri


def upload_file(req):
    context = {"form": UploadFileForm(), "chart_type": ["bar", "line", "pie"]}

    if req.method == "POST":
        form = UploadFileForm(req.POST, req.FILES)
        chart_type = req.POST.get("chart_type", "bar")
        if form.is_valid():
            df = handle_uploaded_file(req.FILES['file'])

            fig = plt.figure()
            if chart_type == "pie":
                df.iloc[:, 0].value_counts().plot(kind='pie', autopct='%1.1f%%')
            else:
                df.iloc[:, 0].value_counts().plot(kind=chart_type)

            plt.tight_layout()
            chart = plot_to_base64(fig)

            table_head = df.head().to_html(classes='table table-striped', index=False)
            table_head = table_head.replace('text-align: right', 'text-align: left')
            return render(req, 'reports/result.html', {
                'columns': df.columns,
                'head': table_head,
                'chart': chart
            })

    return render(req, 'reports/upload.html', context)


