document.querySelectorAll('form').forEach(form=>{
    form.addEventListener('submit', e=>{
        let inputs = form.querySelectorAll('input[required], select[required]');
        let valid = true;
        inputs.forEach(inp=>{
            if(inp.value.trim() === '') valid = false;
        });
        if(!valid) { e.preventDefault(); alert('Please fill all fields'); }
    });
});
